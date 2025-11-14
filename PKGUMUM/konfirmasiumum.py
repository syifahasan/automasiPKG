import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

def konfirmasiumum():
    profile_path = r"E:\ChromeProfileAutomation"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            channel="chrome",
            headless=False
        )

        page = browser.new_page()
        page.goto("https://sehatindonesiaku.kemkes.go.id", wait_until="load")

        while True:
            try:
                page.click("section.fixed >> text='CKG Umum'")
                page.click("text='Cari/Daftarkan Individu'")

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
                        break

                    if h < total_halaman - 1:
                        next_button = page.locator("ul.vpagination li.page-item a.page-link").last
                        next_button.click()
                        page.wait_for_timeout(2000)

            except Exception as e:
                print("❌ Terjadi kesalahan:", str(e))
                break


if __name__ == "__main__":
    konfirmasiumum()