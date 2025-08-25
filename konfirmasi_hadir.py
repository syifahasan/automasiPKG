import pandas as pd
import os
import sys
import time
import math
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

def get_all_sekolah(page):
    # buka dropdown sekolah
    page.click("text=Pilih Sekolah")
    page.wait_for_selector("div.py-2.px-4.cursor-pointer")

    sekolah_list = set()
    dropdown = page.locator("div.py-2.px-4.cursor-pointer")

    prev_count = -1
    while True:
        # ambil semua teks sekolah yang sudah kelihatan
        for text in dropdown.all_inner_texts():
            sekolah_list.add(text.strip())

        # scroll ke elemen terakhir biar load data berikutnya
        last_item = dropdown.nth(dropdown.count() - 1)
        last_item.scroll_into_view_if_needed()
        page.wait_for_timeout(500)  # jeda setengah detik biar data muncul

        # cek kalau tidak ada tambahan sekolah → berarti sudah habis
        if len(sekolah_list) == prev_count:
            break
        prev_count = len(sekolah_list)

    page.click("text=Pilih Sekolah")
    page.wait_for_timeout(300)  # opsional biar lebih natural

    return list(sekolah_list)

def konfirmasi_hadir():
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
        page.click("text=Cari/Daftarkan Individu")

        # page.click("text=Pilih Sekolah")
        # page.wait_for_selector("div.py-2.px-4.cursor-pointer")
        # sekolah_elements = page.locator("div.py-2.px-4.cursor-pointer")
        # sekolah_list = [el.inner_text() for el in sekolah_elements.all()]
        all_sekolah = get_all_sekolah(page)
        print(f"Ditemukan {len(all_sekolah)} sekolah:", all_sekolah)
        kelas_list = [f"Kelas {i}" for i in range(1, 7)]

        for sekolah in all_sekolah:
            print(f"➡ Proses sekolah: {sekolah}")
            # pilih sekolah
            # page.click("label:text('Sekolah')")
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

                konfirmasi_buttons = page.locator("button:has-text('Konfirmasi Hadir')")
                count = konfirmasi_buttons.count()
                if count > 0:
                    print(f"    🔘 Ditemukan {count} peserta belum konfirmasi")
                    for i in range(count):
                        konfirmasi_buttons.first.click()
                        page.wait_for_timeout(500)
                        page.wait_for_selector("div.max-h-full", timeout=5000)
                        page.wait_for_selector("input#verify", timeout=5000)
                        page.click("div.check")
                        
                        hadir_btn = page.locator("button:has(div.tracking-wide:has-text('Hadir'))").last
                        hadir_btn.click()
                        if page.wait_for_selector("button.w-fill >> text=Tutup", timeout=3000):
                            page.click("button.w-fill >> text=Tutup")
                        else:
                            print(f"❓ Tidak ada tombol 'Tutup' atau modal error")
                        time.sleep(2)
                else:
                    print(f"    ✅ Tidak ada peserta belum konfirmasi")

if __name__ == "__main__":
    konfirmasi_hadir()