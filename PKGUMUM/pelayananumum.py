import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

def pelayananumum():
    profile_path = r"E:\ChromeProfileAutomation"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            channel="chrome",
            headless=False
        )

        page = browser.new_page()
        page.goto("https://sehatindonesiaku.kemkes.go.id", wait_until="load")
        page.click("section.fixed >> text='CKG Umum'")
        page.click("text='Pelayanan'")

        try:
            modal_locator = page.locator("div.p-2:has-text('Pengaturan Pelayanan')")
            modal_muncul = modal_locator.wait_for(state="visible", timeout=5000)
            if modal_muncul is not None:
                print("🟢 Modal Pengaturan Pelayanan terdeteksi, klik tombol Simpan...")
                page.locator("button:has-text('Simpan')").click()
                print("✅ Tombol Simpan diklik.")
        except PlaywrightTimeoutError:
            # Kalau modal tidak muncul dalam 5 detik
            print("ℹ️ Modal Pengaturan Pelayanan tidak muncul, lanjut ke proses berikutnya.")
        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat memproses modal: {e}")

        buttons = page.locator("ul >> li")
        last_page_text = buttons.nth(-2).inner_text()

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

            belum_diperiksa_rows = page.locator("div:has-text('Belum Pemeriksaan')")

            
            belum_diperiksa_locators = page.get_by_text("Belum Pemeriksaan")
            count = belum_diperiksa_locators.count()

            if count > 0:
                print(f"    🔘 Ditemukan {count} peserta belum di periksa")
                rows = page.locator("table tbody tr")

                for i in range(rows.count()):
                    row = rows.nth(i)
                    status = row.locator("td").filter(has_text="Belum Pemeriksaan")
                    if status.count() > 0:
                         tombol_mulai = row.locator("button:has(div.tracking-wide:has-text('Mulai'))")
                         if tombol_mulai.count() > 0:
                            tombol_mulai.first.click()
                            page.wait_for_timeout(1500)
                            btn_selesai = page.locator("button:has(div.tracking-wide:has-text('Selesaikan Layanan'))")
                            btn_mulai = page.locator("button:has(div.tracking-wide:has-text('Mulai Pemeriksaan'))")
                            if btn_mulai.is_visible():
                                print("🔘 Tombol 'Mulai Pemeriksaan' ditemukan → klik dulu")
                                btn_mulai.click()
                                page.wait_for_timeout(1000)
                                page.wait_for_selector("text=Konfirmasi Tanggal Pemeriksaan").is_visible()
                                page.locator("button:has-text('Simpan')").click()
                            elif btn_selesai.is_visible():
                                print("✅ Sudah di halaman pemeriksaan, tombol 'Selesaikan Layanan' tersedia → langsung isi form")
                            else:
                                print("⚠️ Tidak ditemukan tombol pemeriksaan, skip peserta ini")
                                continue
                            page.wait_for_timeout(1000)
                    
            else:
                print("    ℹ️ Tidak ada peserta dengan status 'Belum Pemeriksaan' di halaman ini")

            
            if h < total_halaman - 1:
                        next_button = page.locator("ul.vpagination li.page-item a.page-link").last
                        next_button.click()
                        page.wait_for_timeout(2000)

if __name__ == "__main__":
    pelayananumum()