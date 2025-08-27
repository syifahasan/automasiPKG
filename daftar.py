import pandas as pd
import os
import sys
import time
import math
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# ====== VALIDASI & BACA EXCEL ======
file_path = "C:/Users/PKM_SJNT/Documents/PKGSEKOLAH/HASIL/SDN DADAP 3/Rekap Hasil Pemeriksaan Kesehatan Anak Sekolah sdn dadap 3.xlsx"

selector_nav_prev = ".mx-icon-double-left"  # tombol mundur tahun
selector_nav_next = ".mx-icon-double-right"  # tombol maju tahun
selector_input_date = "div[class='mx-datepicker']"

bulan_map = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Agt", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
}


try:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    df = pd.read_excel(file_path)
    # GANTI START ROW HARUS
    start_row = 83  # 0-based index, jadi baris 47 = index 46
    start_col = 1   # kolom ke-2 = index 1

    data = df.iloc[start_row:, start_col:]
    # tanggal_list = pd.to_datetime(df.iloc[47, 8], dayfirst=True, errors='coerce')
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

def isi_nik(page, row, index):
    nik = row[6]  # ambil NIK dari kolom ke-7 (index 6)
    
    # cek kosong atau NaN
    if nik is None or str(nik).strip() == "" or (isinstance(nik, float) and math.isnan(nik)):
        print(f"⚠ Data index {index} dilewati karena NIK kosong")
        page.locator("button.absolute.right-4.top-3").click()
        return False   # menandakan dilewati
    
    # isi ke form
    page.fill("input[name='NIK']", str(int(nik)) if isinstance(nik, float) else str(nik))
    return True

def pilih_sekolah(page, nama_sekolah: str):
    # Klik dropdown
    page.click("text='Pilih nama sekolah'")
    page.wait_for_selector("div.modal-content", state="visible")
    
    # Pilih sekolah berdasarkan nama
    page.fill("input[placeholder='Cari nama sekolah']", nama_sekolah)
    page.click(f"div.items-center >> text={nama_sekolah}")
    page.wait_for_selector("div.modal-content", state="hidden")

def no_wa(page, nomor: str):
    nomor_wa = "81522792005"
    if nomor is None or (isinstance(nomor, float) and math.isnan(nomor)) or str(nomor).strip() == "":
        page.fill("input[name='Nomor Whatsapp']", nomor_wa)
        return

    # Pastikan jadi string
    if isinstance(nomor, float):
        nomor = str(int(nomor))  # hilangkan .0
    else:
        nomor = str(nomor)

    # Bersihkan awalan 0
    if nomor.startswith("0"):
        nomor = nomor[1:]

    page.fill("input[name='Nomor Whatsapp']", nomor)

def pilih_jenjang(page, kode_kelas: str):
    # Klik dropdown
    page.click("text='Pilih jenjang pendidikan'")
    page.wait_for_selector("div.modal-content", state="visible")

    kelas = None
    
    # Pilih jenjang berdasarkan kelas
    if kode_kelas == 1:
        kelas = "Kelas 1 "
    elif kode_kelas == 2:
        kelas = "Kelas 2 "
    elif kode_kelas == 3:
        kelas = "Kelas 3 "
    elif kode_kelas == 4:
        kelas = "Kelas 4 "
    elif kode_kelas == 5:
        kelas = "Kelas 5 "
    elif kode_kelas == 6:
        kelas = "Kelas 6 "

    if kelas is None:
        raise ValueError(f"kode_kelas tidak valid: {kode_kelas}")

    page.click(f"div.items-center >> text={kelas}")
    page.wait_for_selector("div.modal-content", state="hidden")

def pilih_jenis_kelamin(page, kode_kelamin: int):
    # Klik dropdown
    page.click("text='Pilih jenis kelamin'")
    page.wait_for_selector("div.cursor-pointer >> text=Laki-laki")
    
    # Mapping kode ke teks di dropdown
    if kode_kelamin == 1 or kode_kelamin == "L":
        page.click("div.cursor-pointer >> text=Laki-laki")
    elif kode_kelamin == 2 or kode_kelamin == "P":
        page.click("div.cursor-pointer >> text=Perempuan")

def disabilitas(page, kode_disabilitas: int):
    # Klik dropdown
    page.click("text='Pilih penyandang disabilitas'")
    page.wait_for_selector("div.cursor-pointer >> text=Tidak memiliki disabilitas")
    
    # Mapping kode ke teks di dropdown
    if kode_disabilitas == 1:
        page.click("div.cursor-pointer >> text=Memiliki disabilitas")
    else :
        page.click("div.cursor-pointer >> text=Tidak memiliki disabilitas")

def pilih_tanggal(page, tanggal: datetime):
    tahun = tanggal.year
    bulan_angka = tanggal.month
    hari = tanggal.day

    page.click("text=Pilih tanggal lahir")
    page.wait_for_selector("div.mx-datepicker-main", state="visible", timeout=5000)
    page.click("text='2025'")

    while True:
        start_year_text = page.inner_text(".mx-calendar-header-label span:nth-child(1)").strip()
        end_year_text = page.inner_text(".mx-calendar-header-label span:nth-child(3)").strip()

        start_year = int(start_year_text)
        end_year = int(end_year_text)
        if tahun < start_year:
            page.click(".mx-icon-double-left")
        elif tahun > end_year:
            page.click(".mx-icon-double-right")
        else:
            break

    page.click(f".mx-calendar-panel-year td.cell[data-year='{tahun}']")
    # 4. Pilih bulan
    data_month = bulan_angka - 1
    page.click(f".mx-calendar-panel-month td.cell[data-month='{data_month}']")

    # 5. Pilih tanggal
    page.click(f"text='{hari}'")



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

        for index, row in data.iterrows():
            page.locator("text=Daftar Baru").first.click()
            page.wait_for_selector("form >> input[name='NIK']", timeout=5000)

            if not isi_nik(page, row, index):
                continue  # langsung lompat ke siswa berikutnya
            page.fill("input[name='Nama']", str(row[0]))      # Kolom kedua setelah start_col
            tgl = pd.to_datetime(row[7])
            pilih_tanggal(page, tgl)
            kode_kelamin = row[1]
            pilih_jenis_kelamin(page, kode_kelamin)
            kode_disabilitas = row[11]
            disabilitas(page, kode_disabilitas)
            nomor = row[10]
            no_wa(page, nomor)
            nama_sekolah = "UPTD SDN 3 DADAP"
            pilih_sekolah(page, nama_sekolah)
            kode_kelas = row[4]
            pilih_jenjang(page, kode_kelas)
            page.check("input[type='checkbox'][id='alamat-sama-dengan-sekolah']", force=True)
            alamat = " ".join(nama_sekolah.split()[3:])
            page.fill("textarea#detail-domisili", str(alamat))

            #input("Tekan ENTER untuk lanjut submit...")
            time.sleep(3)

            page.click("text=Selanjutnya")
            # page.wait_for_load_state("networkidle")

            # Cek apakah tombol "Tutup" ada
            try:
                if page.wait_for_selector("button.w-fill >> text=Tutup", timeout=5000).is_visible():
                    page.click("button.w-fill >> text=Tutup")
                else:
                    raise Exception("Tombol 'Tutup' tidak ada")
            except:
                try:
                    if page.wait_for_selector("text=Terjadi kesalahan", timeout=3000):
                        print(f"⚠ Data index {index} gagal disubmit (Terjadi kesalahan). Skip...")
                        page.click("button.btn-fill-warning")  # Klik OK
                        page.wait_for_selector("div.bg-white:has-text('Formulir Pendaftaran')", timeout=5000)
                        page.locator("button.absolute.right-4.top-3").click()
                except:
                    time.sleep(10)
                    if page.wait_for_selector("button.w-fill >> text=Tutup", timeout=3000):
                        page.click("button.w-fill >> text=Tutup")
                    else:
                        print(f"❓ Tidak ada tombol 'Tutup' atau modal error")

            time.sleep(1)

            # page.click("button.w-fill >> text=Tutup")

            page.wait_for_selector("text=Daftar Baru", state="visible", timeout=5000)
        print("✅ Semua data berhasil diinput")


if __name__ == "__main__":
    daftar_pasien()
