import pandas as pd
import os
import sys
from playwright.sync_api import sync_playwright

# ====== VALIDASI & BACA EXCEL ======
file_path = "C:/Users/PKM_SJNT/Documents/PKGSEKOLAH/HASIL/SDN JUNTIKEBON 1/SDN 1 Juntikebon_kelas 2 4.xlsx"

try:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    df = pd.read_excel(file_path)
    start_row = 47  # 0-based index, jadi baris 47 = index 46
    start_col = 1   # kolom ke-2 = index 1

    data = df.iloc[start_row:, start_col:]
    data = data.reset_index(drop=True)

    if df.empty:
        raise ValueError("File Excel kosong atau tidak ada data yang valid.")

    print("✅ File Excel berhasil dibaca")
    print(f"Jumlah baris: {len(df)}")
    print(df.head())

except (FileNotFoundError, ValueError) as e:
    print(f"⚠️ {e}")
    sys.exit(1)  # Berhenti total

except Exception as e:
    print(f"❌ Terjadi kesalahan saat membaca file: {e}")
    sys.exit(1)


def daftar_pasien():
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

         # Klik button daftar baru
        page.locator("text=Daftar Baru").first.click()

        # Tunggu modal terbuka (misal modal punya role dialog atau class khusus)
        # page.wait_for_selector("div.class_main_modal", state="visible", timeout=5000)

        print("Modal berhasil terbuka")

        for index, row in data.iterrows():
            page.fill("input[name='NIK']", str(row[6]))        # Kolom pertama setelah start_col
            page.fill("input[name='Nama']", str(row[0]))      # Kolom kedua setelah start_col
            
        
        page.wait_for_timeout(1000)

    print("✅ Semua data berhasil diinput")


if __name__ == "__main__":
    daftar_pasien()
