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
        page.wait_for_timeout(1500)  # jeda setengah detik biar data muncul

        # cek kalau tidak ada tambahan sekolah → berarti sudah habis
        if len(sekolah_list) == prev_count:
            break
        prev_count = len(sekolah_list)

    page.click("text=Pilih Sekolah")
    page.wait_for_timeout(500)  # opsional biar lebih natural

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
        #kelas_list = [f"Kelas {i}" for i in range(1, 10)]

        target_sekolah = "UPTD SDN 2 JUNTIKEDOKAN"

        for sekolah in all_sekolah:
            if sekolah != target_sekolah:
                continue  # lewati sekolah lain
            print(f"➡ Proses sekolah: {sekolah}")
            # pilih sekolah
            # page.click("label:text('Sekolah')")
            sekolah_dropdown = page.locator("div.relative.text-black").nth(0)
            sekolah_dropdown.click()
            page.locator("div.py-2.px-4.cursor-pointer", has_text=sekolah).click()

            nama_upper = sekolah.upper()

            if "SMP" in nama_upper or "MTS" in nama_upper:
                kelas_list = [f"Kelas {i}" for i in range(7, 10)]
            elif "SMA" in nama_upper or "SMK" in nama_upper:
                kelas_list = [f"Kelas {i}" for i in range(10, 13)]
            else:
                kelas_list = [f"Kelas {i}" for i in range(1, 7)]  # default SD/MI

            for kelas in kelas_list:
                print(f"  ⬇ Proses kelas {kelas}")
                kelas_dropdown = page.locator("div.relative.text-black").nth(1)
                time.sleep(2)
                kelas_dropdown.click()
                page.locator("div.py-2.px-4.cursor-pointer", has_text=kelas).click()

                page.wait_for_timeout(1500)
                if page.get_by_text("1", exact=True).count() > 0:
                    page.get_by_text("1", exact=True).click()
                    page.wait_for_timeout(2000)
                else:
                    print("⚠ Tidak ada data/pagination untuk kelas ini, skip ke kelas berikutnya")
                    continue
                page.wait_for_timeout(2000)

                # page.wait_for_timeout(2000)
                # ambil semua tombol pagination
                buttons = page.locator("ul >> li")

                # cari teks dari tombol sebelum terakhir (karena terakhir biasanya '>')
                last_page_text = buttons.nth(-2).inner_text()

                # pastikan isinya angka
                if last_page_text.isdigit():
                    total_halaman = int(last_page_text)
                else:
                    # fallback: cari angka terbesar dari semua tombol
                    texts = [b.inner_text() for b in buttons.all()]
                    angka = [int(t) for t in texts if t.isdigit()]
                    total_halaman = max(angka)

                print(f"📑 Total halaman: {total_halaman}")

                for h in range(total_halaman):
                    print(f"➡ Proses halaman {h+1} dari {total_halaman}")

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

                    # pindah halaman dengan tombol NEXT (›), bukan indeks
                    if h < total_halaman - 1:
                        next_button = page.locator("ul.vpagination li.page-item a.page-link").last
                        next_button.click()
                        page.wait_for_timeout(2000)

if __name__ == "__main__":
    konfirmasi_hadir()