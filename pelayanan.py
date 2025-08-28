import pandas as pd
import os
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import math
import konfirmasi_hadir
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

file_path = "C:/Users/PKM_SJNT/Documents/PKGSEKOLAH/HASIL/MII JUNTIKEBON/KELAS 1 5.xlsx"
file_who = "C:/Users/PKM_SJNT/Documents/WHO_IMTU.xlsx"

try:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
    elif not os.path.exists(file_who):
        raise FileNotFoundError(f"File referensi WHO tidak ditemukan: {file_who}")

    df = pd.read_excel(file_path)
    df_who = pd.read_excel(file_who)

    # GANTI START ROW HARUS
    start_row = 10  # 0-based index, jadi baris 47 = index 46
    start_col = 1   # kolom ke-2 = index 1

    data = df.iloc[start_row:, start_col:]
    # tanggal_list = pd.to_datetime(df.iloc[47, 8], dayfirst=True, errors='coerce')
    data = data.reset_index(drop=True)
    data.columns = range(data.shape[1])
    
    if df.empty:
        raise ValueError("File Excel kosong atau tidak ada data yang valid.")
    elif df_who.empty:
        raise ValueError("File referensi WHO kosong atau tidak ada data yang valid.")

    print("✅ File Excel berhasil dibaca")
    print(f"Jumlah baris: {len(df_who)}")
    print(df_who.head())

except (FileNotFoundError, ValueError) as e:
    print(f"⚠️ {e}")
    sys.exit(1)  # Berhenti total

except Exception as e:
    print(f"❌ Terjadi kesalahan saat membaca file: {e}")
    sys.exit(1)

def hitung_status_gizi(umur_bulan, gender, berat, tinggi, df_who):
    # IMT
    imt = berat / ((tinggi/100) ** 2)

    # Cari baris referensi WHO
    row = df_who[(df_who["UmurBulan"]==umur_bulan) & (df_who["Gender"]==gender)]
    if row.empty:
        return None, imt

    m3sd = row["-3SD"].values[0]
    m2sd = row["-2SD"].values[0]
    p1sd = row["+1SD"].values[0]
    p2sd = row["+2SD"].values[0]

    # Klasifikasi
    if imt < m3sd:
        status = "Gizi Buruk"
    elif imt < m2sd:
        status = "Gizi Kurang"
    elif imt <= p1sd:
        status = "Gizi Baik"
    elif imt <= p2sd:
        status = "Gizi Lebih"
    else:
        status = "Obesitas"

    return status, imt

def gizi_anak(page, row, df_who):
    page.locator("button:has(div:has-text('Input Data'))").nth(8).click()
    page.wait_for_timeout(1000)
    try:
        berat = float(row[29])
        tinggi = float(row[30])
        umur_bulan = int(row[8])
        gender = str(row[1])
        print("DEBUG row data:", row.to_dict())

        status, imt = hitung_status_gizi(umur_bulan, gender, berat, tinggi, df_who)
        print(f"🧮 {row[0]} | IMT={imt} → {status}")
        page.fill("input[placeholder='dalam kg']", str(berat))
        page.fill("input[placeholder='dalam cm']", str(tinggi))
        page.locator("select").select_option(status)

        page.click("input[title='Kirim']")
        page.wait_for_timeout(1000)
    except Exception as e:
        print(f"⚠️ Gagal input gizi untuk {row[0]}: {e}")



def pelayanan():
    profile_path = r"E:\ChromeProfileAutomation"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            channel="chrome",
            headless=False
        )

        nama_sekolah = "MIS ISLAMIYAH JUNTIKEBON"

        page = browser.new_page()
        page.goto("https://sehatindonesiaku.kemkes.go.id", wait_until="load")
        page.click("section.fixed >> text=CKG Sekolah")
        page.click("text=Pelayanan")

        # Pilih sekolah manual (satu sekolah per sesi)
        print(f"=== Memproses sekolah: {nama_sekolah} ===")
        sekolah_dropdown = page.locator("div.relative.text-black").nth(0)
        sekolah_dropdown.click()
        page.locator("div.py-2.px-4.cursor-pointer", has_text=nama_sekolah).click()
        time.sleep(1)

        kelas_list = [f"Kelas {i}" for i in range(1, 7)]
        for kelas in kelas_list:
            print(f"  ⬇ Proses kelas {kelas}")
            kelas_dropdown = page.locator("div.relative.text-black").nth(1)
            time.sleep(2)
            kelas_dropdown.click()
            page.locator("div.py-2.px-4.cursor-pointer", has_text=kelas).click()

            page.wait_for_timeout(2000)
            pagination = page.locator("ul.vpagination li.page-item a.page-link")
            total_halaman = pagination.count() or 1
            print(f"📑 Total halaman: {total_halaman}")

            for h in range(total_halaman):
                print(f"➡ Proses halaman {h+1} dari {total_halaman}")
                pelayanan_buttons = page.locator("button:has(div.tracking-wide:has-text('Mulai'))")
                count = pelayanan_buttons.count()
                if count > 0:
                    print(f"  🔘 Ditemukan {count} peserta belum dilayani, memproses...")
                    page.wait_for_selector("table tbody tr")
                    rows = page.locator("table tbody tr")
                    row_count = rows.count()
                    print(f"📋 Jumlah baris peserta di tabel: {row_count}")

                    for i in range(row_count):
                        nama_web = rows.nth(i).locator("td").nth(1).inner_text().strip()
                        print(f"🔎 Cek peserta: {nama_web}")
                        # print(data[0].head())
                        # print(data[0].dtype)

                        # Cari di Excel berdasarkan kolom Nama (anggap ada di kolom ke-1)
                        match = data[data[0].astype(str).str.strip().str.lower() == nama_web.strip().lower()]

                        if match.empty:
                            print(f"   ⏭️ {nama_web} tidak ditemukan di Excel")
                            continue

                        row_excel = match.iloc[0]
                        
                        pelayanan_buttons.nth(i).click()
                        page.wait_for_timeout(1000)
                        mulai_pemeriksaan = page.locator("button:has(div.tracking-wide:has-text('Mulai Pemeriksaan'))")
                        mulai_pemeriksaan.click()
                        page.wait_for_timeout(1000)

                        # Input Data Pemeriksaan Gizi Anak Sekolah
                        gizi_anak(page, row_excel, df_who)






if __name__ == "__main__":
    pelayanan()