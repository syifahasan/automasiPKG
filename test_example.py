from playwright.sync_api import sync_playwright

profile_path = r"E:\ChromeProfileAutomation"  # Lokasi profil automasi kamu

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=profile_path,
        channel="chrome",     # Jalankan Google Chrome asli
        headless=False
    )

    page = browser.new_page()

    # 1. Buka halaman utama website
    page.goto("https://sehatindonesiaku.kemkes.go.id")

    # 2. Hover menu "CKG Sekolah"
    page.click("text=CKG Sekolah")

    # 3. Klik submenu "Pelayanan"
    page.click("text=Pelayanan")

    # 4. Tunggu halaman selesai dimuat
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except:
        print("Timeout networkidle, lanjut saja...")

    print("Berhasil masuk halaman Pelayanan")

    browser.close()
