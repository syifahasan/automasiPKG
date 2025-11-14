import pandas as pd
import os
import sys
import time
import math
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# ====== VALIDASI & BACA EXCEL ======
file_path = "C:/Users/PKM_SJNT/Documents/PKGUMUM/PASIEN HOME VISIT 5-8 NOV 2025.xlsx"

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
    start_row = 13 # 0-based index, jadi baris 47 = index 46
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
    nik = row[3]  # ambil NIK dari kolom ke-7 (index 6)
    
    # cek kosong atau NaN
    if nik is None or str(nik).strip() == "" or (isinstance(nik, float) and math.isnan(nik)):
        print(f"⚠ Data index {index} dilewati karena NIK kosong")
        page.locator("button.absolute.right-4.top-3").click()
        return False   # menandakan dilewati
    
    # isi ke form
    page.fill("input[name='NIK']", str(int(nik)) if isinstance(nik, float) else str(nik))
    return True

def pilih_pekerjaan(page, jenis_kelamin):
    # Klik dropdown
    page.click("text='Pilih pekerjaan'")
    page.wait_for_selector("div.modal-content", state="visible")

     # Tentukan pekerjaan berdasarkan jenis kelamin
    if jenis_kelamin.lower() in ["l", "laki-laki"]:
        pekerjaan = "Wirausaha/Pekerja Mandiri"
    elif jenis_kelamin.lower() in ["p", "perempuan"]:
        pekerjaan = "Ibu Rumah Tangga"
    else:
        pekerjaan = "Lainnya"

    # Klik opsi pekerjaan yang sesuai
    page.get_by_text(pekerjaan, exact=True).click()
    

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
    elif kode_kelas == 7:
        kelas = "Kelas 7 "
    elif kode_kelas == 8:
        kelas = "Kelas 8 "
    elif kode_kelas == 9:
        kelas = "Kelas 9 "
    elif kode_kelas == 10:
        kelas = "Kelas 10 "
    elif kode_kelas == 11:
        kelas = "Kelas 11 "
    elif kode_kelas == 12:
        kelas = "Kelas 12 "

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

def pilih_alamat(page, provinsi, kabupaten, kecamatan, kelurahan_excel):
    # Pilih Provinsi
    page.click("text='Pilih alamat domisili'")
    page.wait_for_selector("div.modal-content", state="visible")
    page.get_by_text(provinsi, exact=True).click()

    # Tunggu Kabupaten muncul, lalu pilih
    page.wait_for_selector("text='Daftar Kabupaten/Kota'")
    page.wait_for_selector("div.modal-content", state="visible")
    page.get_by_text(kabupaten, exact=True).click()

    # Tunggu Kecamatan muncul, lalu pilih
    page.wait_for_selector("text='Daftar Kecamatan'")
    page.wait_for_selector("div.modal-content", state="visible")
    page.get_by_text(kecamatan, exact=True).click()

    # Tunggu Kelurahan muncul, lalu pilih sesuai Excel
    page.wait_for_selector("text='Daftar Kelurahan'")
    page.wait_for_selector("div.modal-content", state="visible")
    page.get_by_text(kelurahan_excel, exact=True).click()

def tanggal_pemeriksaan(page):
    page.wait_for_selector("div.grid.grid-cols-7", state="visible")

    tanggal_buttons = page.locator("button.relative.h-auto")
    today = datetime.today().day
    total_tanggal = tanggal_buttons.count()

    for i in range(total_tanggal):
        button = tanggal_buttons.nth(i)

        # Lewati tanggal yang disabled
        classes = button.get_attribute("class") or ""
        if "cursor-not-allowed" in classes:
            continue

        # Ambil teks tanggal
        tanggal_text = button.locator("span.font-bold").text_content().strip()
        if not tanggal_text.isdigit():
            continue

        tanggal = int(tanggal_text)

        # Lewati tanggal sebelum hari ini
        if tanggal < today:
            continue
        

        # Ambil kuota (angka di bawah tanggal)
        kuota_locator = button.locator("css=[class*='text-[15px]'] span")
        kuota_text = kuota_locator.text_content().strip() if kuota_locator.count() > 0 else "0"
        kuota = int(kuota_text) if kuota_text.isdigit() else 0

        if tanggal == today and kuota <= 10:
            continue  # langsung loncat ke tanggal berikutnya

        if kuota > 10:
            button.click()
            print(f"✅ Memilih tanggal {tanggal} (kuota: {kuota})")
            return
        
        
    
    print("⚠️ Tidak ada tanggal dengan kuota > 10 ditemukan.")



def disabilitas(page, kode_disabilitas: int):
    # Klik dropdown
    page.click("text='Pilih penyandang disabilitas'")
    page.wait_for_selector("div.cursor-pointer >> text=Tidak memiliki disabilitas")
    
    # Mapping kode ke teks di dropdown
    if kode_disabilitas in [0,'0', 'nan', 'NaN', '', 'tidak']:
        page.click("div.cursor-pointer >> text=Tidak memiliki disabilitas")
    else :
        page.click("div.cursor-pointer >> text=Memiliki disabilitas")

def pilih_tanggal(page, tanggal: datetime):
    tahun = tanggal.year
    bulan_angka = tanggal.month
    hari = tanggal.day

    page.click("text=Pilih tanggal lahir")
    page.wait_for_selector("div.mx-calendar-panel-date", state="visible", timeout=5000)
    # page.click("text='2025'")
    try:
        tombol_tahun = page.locator("button.mx-btn-current-year")
        tombol_tahun.click()
    except PlaywrightTimeoutError:
        print("⚠️ Tidak bisa klik tombol tahun, coba ulang...")
        page.click("text=Pilih tanggal lahir")
        page.wait_for_selector("button.mx-btn-current-year", timeout=5000)
        page.locator("button.mx-btn-current-year").click()

    page.wait_for_selector("td.cell[data-year]", state="visible", timeout=5000)

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

    page.click(f"td.cell[data-year='{tahun}']")
        # try:
        #     page.click(f"td.cell[data-year='{tahun}']")
        #     break
        # except PlaywrightTimeoutError:
        #     try:
        #         current_year_text = page.locator("button.mx-btn-current-year").text_content(timeout=2000)
        #         current_year = int(current_year_text)
        #     except:
        #         current_year = tahun  # fallback
        #     if current_year > tahun:
        #         page.click(".mx-icon-double-left")
        #     elif current_year < tahun:
        #         page.click(".mx-icon-double-right")
        #     else:
        #         break

    # 4. Pilih bulan
    data_month = bulan_angka - 1
    page.click(f"td.cell[data-month='{data_month}']")

    # 5. Pilih tanggal
    tanggal_str = tanggal.strftime("%Y-%m-%d")
    page.click(f"td.cell[title='{tanggal_str}']")
    print(f"✅ Tanggal lahir dipilih: {tanggal_str}")



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
        page.click("section.fixed >> text=CKG Umum")
        page.click("text=Cari/Daftarkan Individu")

        for index, row in data.iterrows():
            page.locator("text=Daftar Baru").first.click()
            page.wait_for_selector("form >> input[name='NIK']", timeout=5000)

            if not isi_nik(page, row, index):
                continue  # langsung lompat ke siswa berikutnya
            page.fill("input[name='Nama']", str(row[1]))      # Kolom kedua setelah start_col
            tgl = pd.to_datetime(row[7])
            pilih_tanggal(page, tgl)
            kode_kelamin = row[6]
            pilih_jenis_kelamin(page, kode_kelamin)
            nomor = None
            no_wa(page, nomor)
            # nama_sekolah = "UPTD SDN 2 JUNTIKEDOKAN"
            # pilih_sekolah(page, nama_sekolah)
            pilih_pekerjaan(page, kode_kelamin)
            
            alamat_excel = str(row[13]).title()  # contoh: kolom ke-6 di Excel
            pilih_alamat(page, "Jawa Barat", "Kab. Indramayu", "Juntinyuat", alamat_excel)
            # if pd.isna(alamat_excel) or str(alamat_excel).strip().lower() in ["", "nan"]:
            #     alamat = " ".join(nama_sekolah.split()[3:])
            # else:
            #     alamat = str(alamat_excel).strip()
            # # alamat = " ".join(nama_sekolah.split()[3:])
            # # alamat = "Juntikedokan"
            page.fill("textarea#detail-domisili", alamat_excel)

            tanggal_pemeriksaan(page)

            #input("Tekan ENTER untuk lanjut submit...")
            time.sleep(1)

            page.click("text=Selanjutnya")

            page.locator('button.w-fill >> text=Pilih').click()
            page.locator('div.tracking-wide >> text=Daftarkan dengan NIK ').click()

            if page.locator("div:has-text('Isi Data Wali')").first.is_visible():
                print("🧓 Form wali terdeteksi — pasien lansia.")
                # Centang 'Daftarkan tanpa data wali'
                checkbox = page.locator("input[type='checkbox'][id='noWali']")
                checkbox.scroll_into_view_if_needed()
                checkbox.click(force=True)

                page.locator("button[type='submit']:has-text('Daftar')").click()
                print("📋 Pendaftaran lansia selesai.")
            else:
                print("👤 Tidak ada form wali — pendaftaran langsung selesai.")
                # continue

            page.wait_for_timeout(2000)

            # Cek apakah tombol "Tutup" ada
            try:
                page.wait_for_selector("button.w-fill >> text=Tutup", timeout=10000)
                tombol_tutup = page.locator("button.w-fill >> text=Tutup")
                if tombol_tutup.is_visible():
                    tombol_tutup.click()
                else:
                    raise Exception("Tombol 'Tutup' tidak ada")
            except Exception as e:
                print(f"⚠ Tidak menemukan tombol 'Tutup': {e}")

                if page.locator("text=Terjadi kesalahan").is_visible():
                    print(f"⚠ Data index {index} gagal disubmit (Terjadi kesalahan). Skip...")
                    page.click("button.btn-fill-warning")  # Klik OK
                    page.wait_for_selector("div.bg-white:has-text('Formulir Pendaftaran')", timeout=5000)
                    page.locator("button.absolute.right-4.top-3").click()

                elif page.locator("text=Peserta Menerima Pemeriksaan").is_visible():
                    print(f"⚠ Data index {index} gagal disubmit (Peserta Menerima Pemeriksaan). Skip...")
                    page.click("button.btn-fill-primary:has-text('Kembali')", force=True)
                    # page.click("button.btn-fill-primary")  # Klik Kembali
                    page.wait_for_selector("div.bg-white:has-text('Formulir Pendaftaran')", timeout=5000)
                    page.locator("button.absolute.right-4.top-3").click()

                elif page.locator("text=Data belum sesuai KTP").is_visible():
                    print(f"⚠ Data index {index} gagal disubmit (Peserta Menerima Pemeriksaan). Skip...")
                    page.click("button.btn-fill-primary:has-text('Perbaiki data')", force=True)
                    # page.click("button.btn-fill-primary")  # Klik Kembali
                    page.wait_for_selector("div.bg-white:has-text('Formulir Pendaftaran')", timeout=5000)
                    page.locator("button.absolute.right-4.top-3").click()

                else:
                    print(f"❓ Tidak ada tombol 'Tutup' atau modal error lainnya")

            time.sleep(1)

            # page.click("button.w-fill >> text=Tutup")

            page.wait_for_selector("text=Daftar Baru", state="visible", timeout=5000)
        print("✅ Semua data berhasil diinput")


if __name__ == "__main__":
    daftar_pasien()
