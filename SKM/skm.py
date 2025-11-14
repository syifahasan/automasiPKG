from playwright.sync_api import sync_playwright
import time
import random

def skm():
    profile_path = r"E:\\ChromeProfileAutomation"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False,
            channel="chrome"
        )
        page = browser.new_page()
        page.goto("https://skmindramayu.web.id/puskesmas-juntinyuat/pilih-layanan-opd", wait_until="load")

        while True:
            try:
                # Klik dropdown
                page.locator("span.select2-selection__rendered").click()
                page.wait_for_selector("li.select2-results__option", timeout=5000)
                time.sleep(0.5)

                # Debug - tampilkan opsi
                options = page.locator("li.select2-results__option").all_inner_texts()
                print("Opsi ditemukan:", options)

                # Pilih KLUSTER 1 secara manual + trigger event
                page.evaluate('''() => {
                    const $ = window.jQuery;
                    if ($) {
                        const select = $('select.select2-hidden-accessible');
                        select.val(select.find('option').filter((_, o) => o.text.trim() === "KLUSTER 1").val()).trigger('change').trigger('select2:select');
                    }
                }''')
                page.locator("span.select2-selection__rendered").click()
                page.click("button:has-text('Next')")
                # page.wait_for_selector("input.tanggal_survey", timeout=5000)
                page.locator("label.container_radio:has-text('08.00-12.00')").click()
                # Isi usia
                page.locator("#usia").click()
                page.locator("#usia").fill(str(random.randint(21, 60)))
                page.locator("#usia").press("Tab")

                # Pilih jenis kelamin
                jenis_kelamin = random.choice(["L", "P"])
                page.locator(f"input[name='jenis_kelamin'][value='{jenis_kelamin}']").click()

                # Pilih pendidikan
                pendidikan = random.choice(["SMA", "Diploma", "S1"])
                page.locator("div.form-group", has_text="Pendidikan")\
                    .locator(f"label.container_radio:has-text('{pendidikan}')").click()

                # Pilih pekerjaan
                pekerjaan = random.choice(["PNS", "SWASTA", "WIRAUSAHA"])
                page.locator("div.form-group", has_text="Pekerjaan")\
                    .locator(f"label.container_radio:has-text('{pekerjaan}')").click()

                # Tunggu tombol aktif
                page.locator("button:has-text('Next'):not([disabled])").click()
                
                page.locator("div.review_block_smiles label.smile_5", has_text="Sangat Sesuai").first.click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.locator("div.review_block_smiles label.smile_5", has_text="Sangat Mudah").first.click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.locator("div.review_block_smiles label.smile_5", has_text="Sangat Cepat").first.click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.locator("div.review_block_smiles label.smile_5", has_text="Gratis").first.click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.locator("div.review_block_smiles label.smile_5", has_text="Sangat Sesuai").nth(1).click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.locator("div.review_block_smiles label.smile_5", has_text="Sangat Kompeten").first.click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.locator("div.review_block_smiles label.smile_5", has_text="Sangat Sopan dan Ramah").first.click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.locator("div.review_block_smiles label.smile_5", has_text="Sangat Baik").first.click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.locator("div.review_block_smiles label.smile_5", has_text="Dikelola dengan Baik").first.click()
                page.locator("button:has-text('Next'):not([disabled])").click()

                page.fill("textarea[name='masukan_saran']", "Semua sudah sangat baik, terima kasih!")
                page.click("button:has-text('Submit')")

                # page.wait_for_selector("text=Berhasil Mengisi survei", timeout=5000)
                print("✅ Halaman berhasil terdeteksi, klik tombol Kembali.")

                if page.locator("a.btn-success", has_text="Kembali").is_visible():
                    page.locator("a.btn-success", has_text="Kembali").click()
                    print("↩️ Klik tombol 'Kembali', ulang dari awal...\n")
                else:
                    print("⚠️ Tombol 'Kembali' tidak ditemukan, menghentikan loop.")
                    break

                # Tunggu sebentar agar halaman siap sebelum mengulang
                time.sleep(2)
            except Exception as e:
                print(f"❌ Terjadi error: {e}")
                # Jika error muncul (misalnya elemen tidak ditemukan), tunggu dan coba ulang
                time.sleep(3)
                continue

if __name__ == "__main__":
    skm()
