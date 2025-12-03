import os
import time
import json
import math
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL_SIMPUS = "https://indramayu.epuskesmas.id/"
USERNAME = "deni"
PASSWORD = "Indramayu7."

INPUT_EXCEL = "C:/Users/PKM_SJNT/Documents/REKAP CKG/2025/KLASTER DEWASA LAKI/PKMJNT(L)2025.xlsx"
OUTPUT_DIR = "output_simpus"
OUTPUT_LAPORAN = os.path.join(OUTPUT_DIR, "laporan_validasi.xlsx")
RAW_SCRAPED_JSON = os.path.join(OUTPUT_DIR, "rekammedis_raw.json")

MAX_HISTORY = 10

CONFIG_SELECTORS = {
    "login_username": "input#email",
    "login_password": "input#password",
    "login_submit": "button:has-text('Login')",

    "dropdown_pendaftaran": "a[id='menu_pendaftaran']",
    "menu_pasien_kk": "a#menu_pendaftaran_pasien",

    "search_input": 'input[placeholder="Cari NIK / No Asuransi"]',
    "search_button": "button:has-text('Cari')",

    "result_table_rows": "table tbody tr",
    "result_row_nik_td_index": 6,
    "result_row_name_td_index": 5,

    "history_table_rows": "div.table-responsive table tbody tr",

}

# ------------------------
# Setup logging & output
# ------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


# ------------------------
# Helper functions
# ------------------------
def safe_text_from_locator(locator):
    """Return text from locator or '' if missing"""
    try:
        return locator.inner_text().strip()
    except Exception:
        return ""
    
# ------------------------
# Scraping logic
# ------------------------
def scrape_patient_history(page):
    """
    Mengembalikan list of dict: setiap dict mewakili 1 kunjungan (tanggal, poli, link_detail_locator)
    Kita akan klik setiap entry untuk ambil detail.
    """
    history = []
    try:
        page.wait_for_selector(CONFIG_SELECTORS["history_table_rows"], timeout=3000)
    except PlaywrightTimeoutError:
        return history

    rows = page.locator(CONFIG_SELECTORS["history_table_rows"])
    count = rows.count()
    logging.debug(f"History rows found: {count}")
    for i in range(min(count, MAX_HISTORY)):
        try:
            row = rows.nth(i)
            # contoh: kolom tanggal ada di kolom ke-2, poli di kolom ke-3 => kita ambil text semua kolom
            tds = row.locator("td")
            cells = []
            try:
                nc = tds.count()
                for j in range(nc):
                    cells.append(safe_text_from_locator(tds.nth(j)))
            except Exception:
                pass
            # ambil tombol detail (jika ada)
            detail_btn = ""
            try:
                # gunakan salah satu selector button
                btn = row.locator(CONFIG_SELECTORS["history_row_detail_button"])
                if btn.count() > 0:
                    detail_btn = btn.first
                else:
                    detail_btn = None
            except Exception:
                detail_btn = None

            history.append({
                "row_index": i,
                "cells": cells,
                "detail_btn": detail_btn,
            })
        except Exception as e:
            logging.warning("Error extracting history row: %s", e)
    return history

def scrape_visit_detail(page):
    """
    Scrape pemeriksaan & resep dalam 1 kunjungan (halaman detail terbuka).
    Mengembalikan dict { 'tanggal':..., 'pemeriksaan': {...}, 'obat': [ {name,dosis,qty}, ... ] }
    """
    data = {"pemeriksaan": {}, "obat": []}
    # contoh mencari nilai pemeriksaan seperti gula/tensi/kolesterol
    try:
        # Gula darah (bisa berupa teks atau input)
        try:
            gula_elem = page.locator(CONFIG_SELECTORS["pemeriksaan_gula_selector"])
            if gula_elem.count() > 0:
                data["pemeriksaan"]["gula_darah"] = safe_text_from_locator(gula_elem.first)
        except Exception:
            data["pemeriksaan"]["gula_darah"] = None

        # Tensi sistolik & diastolik
        try:
            s_elem = page.locator(CONFIG_SELECTORS["pemeriksaan_tensi_sistolik"])
            d_elem = page.locator(CONFIG_SELECTORS["pemeriksaan_tensi_diastolik"])
            if s_elem.count() > 0:
                data["pemeriksaan"]["tensi_sistolik"] = safe_text_from_locator(s_elem.first)
            if d_elem.count() > 0:
                data["pemeriksaan"]["tensi_diastolik"] = safe_text_from_locator(d_elem.first)
        except Exception:
            pass

        # Kolesterol
        try:
            kol_elem = page.locator(CONFIG_SELECTORS["pemeriksaan_kolesterol"])
            if kol_elem.count() > 0:
                data["pemeriksaan"]["kolesterol_total"] = safe_text_from_locator(kol_elem.first)
        except Exception:
            pass

    except Exception as e:
        logging.warning("Error scraping pemeriksaan: %s", e)

    # ambil obat (tabel resep)
    try:
        obat_rows = page.locator(CONFIG_SELECTORS["visit_tbl_obat_rows"])
        for r in range(obat_rows.count()):
            try:
                row = obat_rows.nth(r)
                tds = row.locator("td")
                # coba ambil kolom nama/dosis/qty dengan fallback
                name = safe_text_from_locator(tds.nth(0)) if tds.count() > 0 else ""
                dose = safe_text_from_locator(tds.nth(1)) if tds.count() > 1 else ""
                qty = safe_text_from_locator(tds.nth(2)) if tds.count() > 2 else ""
                # bersihkan:
                if name == "":
                    # kadang nama di td2
                    name = safe_text_from_locator(tds.nth(1)) if tds.count() > 1 else name
                data["obat"].append({"nama": name, "dosis": dose, "qty": qty})
            except Exception:
                continue
    except Exception:
        pass

    return data

# Main worker per pasien
# ------------------------
def process_patient(page, nik, excel_row):
    result = {
        "nik": nik,
        "found": False,
        "message": "",
        "history_summary": [],
        "history_details": []
    }

    try:
        # --- pilih input pencarian ---
        search_input = page.locator(CONFIG_SELECTORS["search_input"]).first

        # fokus ke input
        search_input.click()

        # CLEAR: Ctrl+A lalu Delete (pastikan NIK lama benar2 hilang)
        try:
            search_input.press("Control+A")
        except Exception:
            pass
        search_input.press("Delete")

        # KETIK NIK baru pelan-pelan supaya event JS kepanggil semua
        search_input.type(str(nik), delay=80)

        # 🔴 PENTING: paksa trigger event change/blur
        # agar script SIMPUS update variabel internal NIK
        search_input.evaluate("el => el.blur()")
        page.wait_for_timeout(150)  # jeda kecil

        # klik tombol CARI
        try:
            page.locator(CONFIG_SELECTORS["search_button"]).click()
        except Exception:
            page.click("text=Cari")

        # tunggu sampai tabel benar-benar menampilkan hasil
        try:
            page.wait_for_function(
                """
                () => {
                    const tbody = document.querySelector('table tbody');
                    if (!tbody) return false;
                    const txt = tbody.innerText.trim().toLowerCase();
                    return txt.length > 0;
                }
                """,
                timeout=7000
            )
        except PlaywrightTimeoutError:
            page.wait_for_timeout(2000)

    except Exception as e:
        result["message"] = f"Error saat pencarian: {e}"
        return result

    # --- lanjut logika lama: cek rows, 'Data tidak ditemukan', klik nama, dst ---
    try:
        rows = page.locator(CONFIG_SELECTORS["result_table_rows"])
        row_count = rows.count()

        if row_count == 0:
            result["found"] = False
            result["message"] = "Tidak ada baris hasil (tabel kosong)"
            return result

        first = rows.nth(0)
        row_text = first.inner_text().strip().lower()

        if row_count == 1 and "data tidak ditemukan" in row_text:
            result["found"] = False
            result["message"] = "Data tidak ditemukan di SIMPUS untuk NIK ini"
            print(result["message"])
            return result

        # klik nama pasien untuk buka detail
        name_idx = CONFIG_SELECTORS["result_row_name_td_index"]
        time.sleep(0.5)
        first.locator(f"td:nth-child({name_idx})").dblclick()
        result["found"] = True
        result["message"] = "Ditemukan"

        # ... lanjut scrap riwayat, dll ...
        history_rows = scrape_patient_history(page)
        # untuk setiap history rows, klik detail jika ada & scrap visit detail
        for h in history_rows:
            entry = {"cells": h["cells"], "pemeriksaan": {}, "obat": []}
            # klik detail button jika ada
            try:
                if h["detail_btn"] and hasattr(h["detail_btn"], "click"):
                    h["detail_btn"].click()
                    # tunggu load
                    time.sleep(0.6)
                    # scrap visit detail
                    visit = scrape_visit_detail(page)
                    entry["pemeriksaan"] = visit["pemeriksaan"]
                    entry["obat"] = visit["obat"]
                    # kembali ke halaman pasien agar bisa klik entry berikutnya
                    # biasanya ada tombol Back atau breadcumb. Kita gunakan history back:
                    try:
                        page.go_back()
                        time.sleep(0.4)
                    except Exception:
                        # jika tidak bisa back, reload pasien detail URL:
                        page.reload()
                        time.sleep(0.6)
                else:
                    # kalau tidak ada tombol detail (mungkin table row sudah memuat ringkasan)
                    # kita tetap simpan cells
                    pass
            except PlaywrightTimeoutError as e:
                logging.warning("Timeout on clicking detail: %s", e)
            except Exception as e:
                logging.warning("Error while clicking detail: %s", e)

            result["history_summary"].append(entry["cells"])
            result["history_details"].append({"pemeriksaan": entry["pemeriksaan"], "obat": entry["obat"]})

        # selesai untuk pasien ini
    except Exception as e:
        logging.error("Error saat mengakses hasil pencarian / detail pasien: %s", e)
        result["message"] = f"Error extracting patient details: {e}"


def main():
    profile_path = r"E:\ChromeProfileAutomation"
    logging.info("Mulai proses validasi SIMPUS")
    # baca excel
    df = pd.read_excel(INPUT_EXCEL, dtype=str)
    # pastikan kolom NIK ada
    if 'NIK' not in df.columns:
        logging.error("Kolom 'NIK' tidak ditemukan di Excel input. Pastikan kolom bernama 'NIK'.")
        return

    # list unique NIK
    nik_list = df['NIK'].dropna().astype(str).unique().tolist()
    logging.info("Jumlah NIK unik di file: %d", len(nik_list))

    scraped_results = []

    with sync_playwright() as p:
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            channel="chrome",
            headless=False
        )
        # context = browser.new_context()
        page = browser.new_page()
        page.set_default_timeout(7000)

        # --- LOGIN ---
        logging.info("Membuka URL SIMPUS: %s", URL_SIMPUS)
        page.goto(URL_SIMPUS)
        try:
            if page.locator('#menu_user').first.is_visible():
                logging.info("Sudah login, skip proses login.")
                # klik puskesmas jika perlu
                goto_dashboard = True
            else:
                goto_dashboard = False
        except:
            goto_dashboard = False
        if not goto_dashboard:
            logging.info("Melakukan login otomatis...")
            try:
                page.locator('li:has-text("Infokes Manajemen Pasien ™")').first.click()
                page.locator('a:has-text("ePuskesmas")').first.click()
                page.wait_for_timeout(1000)

                page.fill(CONFIG_SELECTORS["login_username"], USERNAME)
                page.fill(CONFIG_SELECTORS["login_password"], PASSWORD)
                page.click(CONFIG_SELECTORS["login_submit"])
                page.wait_for_timeout(1500)

                # klik puskesmas setelah login
                page.locator('button:has-text(" PUSKESMAS JUNTINYUAT")').first.click()
                logging.info("Login berhasil.")
            except Exception as e:
                logging.warning("Gagal login otomatis: %s", e)

        # langsung ke menu Pendaftaran -> Pasien & KK
        try:
            # hover menu
            page.click(CONFIG_SELECTORS["dropdown_pendaftaran"])
            time.sleep(0.2)
            page.click(CONFIG_SELECTORS["menu_pasien_kk"])
            time.sleep(0.8)
        except Exception:
            logging.warning("Gagal membuka menu Pendaftaran/Pasien & KK: periksa selector menu.")

        # sekarang kita di halaman pasien — mulailah loop NIK
        for nik in tqdm(nik_list, desc="Processing NIKs"):
            try:
                # proses pasien
                res = process_patient(page, nik, df)
                scraped_results.append(res)
                # after each patient, navigate back to pasien list to search next
                try:
                    # jika ada breadcumb atau link kembali, bisa klik, disini kita reload the pasien listing page
                    page.reload()
                    time.sleep(0.5)
                    # kembali ke menu Pasien & KK jika reload bukan di halaman listing
                    # (opsional) page.click("text=Pasien & KK")
                except Exception:
                    pass
                # sediakan jeda supaya server tidak terasa diserang
                time.sleep(0.3)
            except Exception as e:
                 logging.error("Error processing NIK %s: %s", nik, e)

    #     # close browser
        browser.close()

    # # setelah semua, bandingkan dan tulis laporan
    # df_report, all_raw = compare_and_write_report(df, scraped_results)

    # # buat plot
    # plot_dir = make_plots_from_raw(all_raw, df)

    # logging.info("Selesai. Laporan: %s, Plots di: %s", OUTPUT_LAPORAN, plot_dir)

if __name__ == "__main__":
    main()
