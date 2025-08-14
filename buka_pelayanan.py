from playwright.sync_api import sync_playwright
import time

def run_script():
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

         # Klik dropdown "Pilih Sekolah"
        page.click("text=Pilih sekolah")  # selector tergantung struktur HTML

        # Scroll sampai sekolah yang dimau terlihat
        school_target = page.locator("div:has-text('UPTD SDN 1 JUNTIKEBON')").last
        school_target.scroll_into_view_if_needed()


        # 3. Klik sekolah target
        school_target.click()

        print(f"Berhasil memilih sekolah: {school_target.text_content}")


        #PILIH KELAS
        page.click("text=Semua kelas")
        class_target = page.locator("div:has-text('Kelas 2')").last
        class_target.scroll_into_view_if_needed()

        class_target.click()

        page.click("div.w-full >> text=Selesai Pemeriksaan")


if __name__ == "__main__":
    run_script()
