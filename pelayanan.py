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

def get_data_from_sheets(sheet_url, worksheet_name):
    # Scope akses Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Ambil worksheet
    sheet = client.open_by_url(sheet_url).worksheet(worksheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def pelayanan(sheet_url="https://docs.google.com/spreadsheets/d/1aERk1TbBtqnXlc2EwAXvxZL9DPIJPrFjeYqjtKwgg9I/edit?gid=346604644#gid=346604644", worksheet_name="Register Per Nama Anak SD (2)"):

    # Ambil data dari Google Sheets
    df = get_data_from_sheets(sheet_url, worksheet_name)

    profile_path = r"E:\ChromeProfileAutomation"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            channel="chrome",
            headless=False
        )

        page = browser.new_page()
        page.goto("https://sehatindonesiaku.kemkes.go.id", wait_until="load")
        page.click("section.fixed >> text=CKG Sekolah")
        page.click("text=Pelayanan")

        
        all_sekolah = konfirmasi_hadir.get_all_sekolah(page)
        print(f"Ditemukan {len(all_sekolah)} sekolah:", all_sekolah)
        kelas_list = [f"Kelas {i}" for i in range(1, 7)]
        for sekolah in all_sekolah:
            print(f"\n=== Memproses sekolah: {sekolah} ===")
            # pilih sekolah
            sekolah_dropdown = page.locator("div.relative.text-black").nth(0)
            sekolah_dropdown.click()
            page.locator("div.py-2.px-4.cursor-pointer", has_text=sekolah).click()

            for kelas in kelas_list:
                print(f"  ⬇ Proses kelas {kelas}")
                kelas_dropdown = page.locator("div.relative.text-black").nth(1)
                time.sleep(2)
                kelas_dropdown.click()
                page.locator("div.py-2.px-4.cursor-pointer", has_text=kelas).click()

                page.wait_for_timeout(2000)
                pagination = page.locator("ul.vpagination li.page-item a.page-link")
                total_halaman = pagination.count()
                if total_halaman == 0:
                    total_halaman = 1  # fallback kalau cuma 1 halaman

                print(f"📑 Total halaman: {total_halaman}")

                for h in range(total_halaman):
                    print(f"➡ Proses halaman {h+1} dari {total_halaman}")
                    pelayanan_buttons = page.locator("button:has(div.tracking-wide:has-text('Mulai'))")
                    count = pelayanan_buttons.count()
                    if count > 0:
                        print(f"  🔘 Ditemukan {count} peserta belum dilayani, memproses...")



if __name__ == "__main__":
    pelayanan()