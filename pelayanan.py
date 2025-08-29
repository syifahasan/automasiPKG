import pandas as pd
import os
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import random
import math
import konfirmasi_hadir
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

file_path = "C:/Users/PKM_SJNT/Documents/PKGSEKOLAH/HASIL/MII JUNTIKEBON/KELAS 1 5.xlsx"
file_who = "C:/Users/PKM_SJNT/Documents/WHO_IMTU.xlsx"

try:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
    elif not os.path.exists(file_who):
        raise FileNotFoundError(f"File referensi WHO tidak ditemukan: {file_who}")

    df = pd.read_excel(file_path)
    df_who = pd.read_excel(file_who)

    # GANTI START ROW HARUS
    start_row = 10  # 0-based index, jadi baris 47 = index 46
    start_col = 1   # kolom ke-2 = index 1

    data = df.iloc[start_row:, start_col:]
    # tanggal_list = pd.to_datetime(df.iloc[47, 8], dayfirst=True, errors='coerce')
    data = data.reset_index(drop=True)
    data.columns = range(data.shape[1])
    
    if df.empty:
        raise ValueError("File Excel kosong atau tidak ada data yang valid.")
    elif df_who.empty:
        raise ValueError("File referensi WHO kosong atau tidak ada data yang valid.")

    print("✅ File Excel berhasil dibaca")
    print(f"Jumlah baris: {len(df_who)}")
    print(df_who.head())

except (FileNotFoundError, ValueError) as e:
    print(f"⚠️ {e}")
    sys.exit(1)  # Berhenti total

except Exception as e:
    print(f"❌ Terjadi kesalahan saat membaca file: {e}")
    sys.exit(1)

def hitung_status_gizi(umur_bulan, gender, berat, tinggi, df_who):
    # IMT
    imt = berat / ((tinggi/100) ** 2)

    # Cari baris referensi WHO
    row = df_who[(df_who["UmurBulan"]==umur_bulan) & (df_who["Gender"]==gender)]
    if row.empty:
        return None, imt

    m3sd = row["-3SD"].values[0]
    m2sd = row["-2SD"].values[0]
    p1sd = row["+1SD"].values[0]
    p2sd = row["+2SD"].values[0]

    # Klasifikasi
    if imt < m3sd:
        status = "Gizi Buruk"
    elif imt < m2sd:
        status = "Gizi Kurang"
    elif imt <= p1sd:
        status = "Gizi Baik"
    elif imt <= p2sd:
        status = "Gizi Lebih"
    else:
        status = "Obesitas"

    return status, imt

def gizi_anak(page, row, df_who):
    page.locator("button:has(div:has-text('Input Data'))").nth(8).click()
    page.wait_for_timeout(1000)
    try:
        berat = float(row[29])
        tinggi = float(row[30])
        umur_bulan = int(row[8])
        gender = str(row[1])
        print("DEBUG row data:", row.to_dict())

        status, imt = hitung_status_gizi(umur_bulan, gender, berat, tinggi, df_who)
        print(f"🧮 {row[0]} | IMT={imt} → {status}")
        page.fill("input[placeholder='dalam kg']", str(berat))
        page.fill("input[placeholder='dalam cm']", str(tinggi))
        page.locator("#sq_102i").click()
        page.wait_for_timeout(1000)
        #page.locator(f"ul.sv-list li:has-text('{status}')").click()
        page.locator(f"div[title='{status}']").click()

        page.locator(f"input[title='Kirim']").click()
        page.wait_for_timeout(3000)
    except Exception as e:
        print(f"⚠️ Gagal input gizi untuk {row[0]}: {e}")

def tensi_siswa(page, row):
    page.locator("button:has(div:has-text('Input Data'))").nth(9).click()
    page.wait_for_timeout(1000)
    try:
        tensi_raw = str(row[38]).strip()
        gender = str(row[1]).strip().lower()

        if tensi_raw and tensi_raw.lower() != 'nan':
            parts = tensi_raw.split('/')
            if len(parts) == 2:
                tensi_sistolik = int(parts[0].strip())
                tensi_diastolik = int(parts[1].strip())
            else:
                raise ValueError("Format tensi tidak valid")
        else:
            if gender == 'l':
                tensi_sistolik, tensi_diastolik = 80, 60
            else:
                tensi_sistolik, tensi_diastolik = 75, 60
    
        print(f"🧮 Tensi: {tensi_sistolik}/{tensi_diastolik} mmHg")
        page.fill("#sq_100i", str(tensi_sistolik))
        page.fill("#sq_101i", str(tensi_diastolik))
        page.locator(f"input[title='Kirim']").click()
        page.wait_for_timeout(3000)
    except Exception as e:
        print(f"⚠️ Gagal input tensi untuk {row[0]}: {e}")

def gigi_siswa(page, row):
    page.locator("button:has(div:has-text('Input Data'))").nth(10).click()
    page.wait_for_timeout(1000)
    try:
        kondisi_gigi = str(row[56]).strip().lower()
        if kondisi_gigi in ['', 'nan', '0', 'tidak ada']:
            pilihan = 'Tidak ada'
            radio_id = "sq_100i_0"
        elif kondisi_gigi == '1' :
            pilihan = '1'
            radio_id = "sq_100i_1"
        elif kondisi_gigi == '2':
            pilihan = '2'
            radio_id = "sq_100i_2"
        elif kondisi_gigi == '3':
            pilihan = '3'
            radio_id = "sq_100i_3"
        elif kondisi_gigi in ['lebih dari 3', '>3', '4', '5', '6', '7', '8', '9', '10']:
            pilihan = '>3'
            radio_id = "sq_100i_4"
        else:
            pilihan = random.choice(['1', '2', '3'])
            if pilihan == "1":
                radio_id = "sq_100i_1"
            elif pilihan == "2":
                radio_id = "sq_100i_2"
            else:
                radio_id = "sq_100i_3"

        print(f"🧮 Kondisi Gigi: {kondisi_gigi} → {pilihan}")
        page.locator(f"label[for='{radio_id}']").click()
        page.wait_for_timeout(1000)

        page.locator(f"input[title='Kirim']").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        print(f"⚠️ Gagal input gigi untuk {row[0]}: {e}")

def mata_telinga_siswa (page, row):
    page.locator("button:has(div:has-text('Input Data'))").nth(11).click()
    page.wait_for_timeout(1000)
    try:
        kacamata = str(row[54]).strip().lower()
        tajam_pendengaran = str(row[43]).strip().lower()
        serumen_impaksi = str(row[46]).strip().lower()
        infeksi_telinga = str(row[48]).strip().lower()
        mata_luar = str(row[50]).strip().lower()
        visus_mata = str(row[52]).strip().lower()

        #tajam pendengaran
        if tajam_pendengaran in ['', 'nan', 'normal', 'tidak ada', '1', 'ya']:
            pilihan_telinga = 'Normal'
            radio_id_tajam_kanan = "sq_100i_0"
            radio_id_tajam_kiri = "sq_101i_0"

        page.locator(f"label[for='{radio_id_tajam_kanan}']").click()
        page.locator(f"label[for='{radio_id_tajam_kiri}']").click()
        page.wait_for_timeout(1000)

        print(f"🧮 Kondisi Mata: {tajam_pendengaran} → {pilihan_telinga}")

        #Serumen Impaksi
        if serumen_impaksi in ['1', 'ya', 'ada']:
            pilihan_serumen = 'Ada serumen impaksi'
            radio_id_serumen_kanan = "sq_102i_1"
            radio_id_serumen_kiri = "sq_103i_1"
        elif serumen_impaksi == 'kanan':
            pilihan_serumen = 'Ada serumen impaksi'
            radio_id_serumen_kanan = "sq_102i_1"
            radio_id_serumen_kiri = "sq_103i_0"
        elif serumen_impaksi == 'kiri':
            pilihan_serumen = 'Ada serumen impaksi'
            radio_id_serumen_kiri = "sq_103i_1"
            radio_id_serumen_kanan = "sq_102i_0"
        elif serumen_impaksi in ['0', 'tidak ada', 'nan', 'tidak']:
            pilihan_serumen = 'Tidak ada serumen impaksi'
            radio_id_serumen_kanan = "sq_102i_0"
            radio_id_serumen_kiri = "sq_103i_0"
        else:
            pilihan_serumen = 'Ada serumen impaksi'
            radio_id_serumen_kanan = "sq_102i_1"
            radio_id_serumen_kiri = "sq_103i_1"

        page.locator(f"label[for='{radio_id_serumen_kanan}']").click()
        page.locator(f"label[for='{radio_id_serumen_kiri}']").click()
        print(f"🧮 Kondisi Telinga: {pilihan_serumen}")

        #Infeksi Telinga
        if infeksi_telinga in ['0', 'nan', 'tidak']:
            pilihan_infeksi = 'Tidak ada infeksi telinga'
            radio_id_infeksi_kanan = "sq_104i_0"
            radio_id_infeksi_kiri = "sq_105i_0"
        elif infeksi_telinga == 'kanan':
            pilihan_infeksi = 'Ada infeksi telinga'
            radio_id_infeksi_kanan = "sq_104i_1"
            radio_id_infeksi_kiri = "sq_105i_0"
        elif infeksi_telinga == 'kiri':
            pilihan_infeksi = 'Ada infeksi telinga'
            radio_id_infeksi_kiri = "sq_105i_1"
            radio_id_infeksi_kanan = "sq_104i_0"
        else:
            pilihan_infeksi = 'Ada infeksi telinga'
            radio_id_infeksi_kanan = "sq_104i_1"
            radio_id_infeksi_kiri = "sq_105i_1"
        
        page.locator(f"label[for='{radio_id_infeksi_kanan}']").click()
        page.locator(f"label[for='{radio_id_infeksi_kiri}']").click()
        print(f"🧮 Kondisi Telinga: {infeksi_telinga} → {pilihan_infeksi}")

        #Mata Luar
        if mata_luar in ['0', 'nan', 'tidak ada', 'normal', 'tidak']:
            pilihan_mata_luar = 'Tidak'
            radio_id_mata_luar_kanan = "sq_106i_0"
            radio_id_mata_luar_kiri = "sq_107i_0"
        elif mata_luar == 'kanan':
            pilihan_mata_luar = 'Ada kelainan mata luar'
            radio_id_mata_luar_kanan = "sq_106i_1"
            radio_id_mata_luar_kiri = "sq_107i_0"
        elif mata_luar == 'kiri':
            pilihan_mata_luar = 'Ada kelainan mata luar'
            radio_id_mata_luar_kiri = "sq_107i_1"
            radio_id_mata_luar_kanan = "sq_106i_0"
        else:
            pilihan_mata_luar = 'Ada kelainan mata luar'
            radio_id_mata_luar_kanan = "sq_106i_1"
            radio_id_mata_luar_kiri = "sq_107i_1"

        page.locator(f"label[for='{radio_id_mata_luar_kanan}']").click()
        page.locator(f"label[for='{radio_id_mata_luar_kiri}']").click()
        print(f"🧮 Kondisi Mata Luar: {mata_luar} → {pilihan_mata_luar}")

        #Visus Mata
        if visus_mata in ['', 'nan', 'normal', 'tidak ada', '0']:
            pilihan_visus = 'Visus 6/6 - 6/9'
            radio_id_visus_kanan = "sq_108i_1"
            radio_id_visus_kiri = "sq_109i_1"
        elif visus_mata in ['kiri']:
            pilihan_visus = 'Rabun'
            radio_id_visus_kanan = "sq_108i_1"
            radio_id_visus_kiri = "sq_109i_0"
        elif visus_mata in ['kanan']:
            pilihan_visus = 'Rabun'
            radio_id_visus_kanan = "sq_108i_0"
            radio_id_visus_kiri = "sq_109i_1"
        else:
            pilihan_visus = 'Visus 6/6 - 6/9'
            radio_id_visus_kanan = "sq_108i_1"
            radio_id_visus_kiri = "sq_109i_1"
        
        page.locator(f"label[for='{radio_id_visus_kanan}']").click()
        page.locator(f"label[for='{radio_id_visus_kiri}']").click()
        print(f"🧮 Kondisi Visus: {visus_mata} → {pilihan_visus}")

        #Penggunaan Kacamata
        if kacamata in ['0', 'nan', 'tidak', 'tidak ada', '']:
            pilihan_kacamata = 'Tidak'
            radio_id_kacamata = "sq_110i_0"
        else:
            pilihan_kacamata = 'Ya'
            radio_id_kacamata = "sq_110i_1"
        page.locator(f"label[for='{radio_id_kacamata}']").click()
        print(f"🧮 Penggunaan Kacamata: {kacamata} → {pilihan_kacamata}")
        page.wait_for_timeout(1000)
        page.locator(f"input[title='Kirim']").click()
        page.wait_for_timeout(3000)


    except Exception as e:
        print(f"⚠️ Gagal input skrining Telinga dan Mata untuk {row[0]}: {e}")

def pelayanan():
    profile_path = r"E:\ChromeProfileAutomation"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            channel="chrome",
            headless=False
        )

        nama_sekolah = "MIS ISLAMIYAH JUNTIKEBON"

        page = browser.new_page()
        page.goto("https://sehatindonesiaku.kemkes.go.id", wait_until="load")
        
        while True:
            try:
                page.click("section.fixed >> text=CKG Sekolah")
                page.click("text=Pelayanan")
                # Pilih sekolah manual (satu sekolah per sesi)
                print(f"=== Memproses sekolah: {nama_sekolah} ===")
                sekolah_dropdown = page.locator("div.relative.text-black").nth(0)
                sekolah_dropdown.click()
                page.locator("div.py-2.px-4.cursor-pointer", has_text=nama_sekolah).click()
                time.sleep(1)

                kelas_list = [f"Kelas {i}" for i in range(1, 7)]
                for kelas in kelas_list:
                    print(f"  ⬇ Proses kelas {kelas}")
                    kelas_dropdown = page.locator("div.relative.text-black").nth(1)
                    time.sleep(2)
                    kelas_dropdown.click()
                    page.locator("div.py-2.px-4.cursor-pointer", has_text=kelas).click()

                    page.wait_for_timeout(2000)
                    pagination = page.locator("ul.vpagination li.page-item a.page-link")
                    total_halaman = pagination.count() or 1
                    print(f"📑 Total halaman: {total_halaman}")

                    for h in range(total_halaman):
                        print(f"➡ Proses halaman {h+1} dari {total_halaman}")
                        pelayanan_buttons = page.locator("button:has(div.tracking-wide:has-text('Mulai'))")
                        count = pelayanan_buttons.count()
                        if count > 0:
                            print(f"  🔘 Ditemukan {count} peserta belum dilayani, memproses...")
                            page.wait_for_selector("table tbody tr")
                            rows = page.locator("table tbody tr")
                            row_count = rows.count()
                            print(f"📋 Jumlah baris peserta di tabel: {row_count}")

                            for i in range(row_count):
                                nama_web = rows.nth(i).locator("td").nth(1).inner_text().strip()
                                print(f"🔎 Cek peserta: {nama_web}")
                                # print(data[0].head())
                                # print(data[0].dtype)

                                # Cari di Excel berdasarkan kolom Nama (anggap ada di kolom ke-1)
                                match = data[data[0].astype(str).str.strip().str.lower() == nama_web.strip().lower()]

                                if match.empty:
                                    print(f"   ⏭️ {nama_web} tidak ditemukan di Excel")
                                    continue

                                row_excel = match.iloc[0]
                                
                                pelayanan_buttons.nth(i).click()
                                page.wait_for_timeout(1000)
                                mulai_pemeriksaan = page.locator("button:has(div.tracking-wide:has-text('Mulai Pemeriksaan'))")
                                mulai_pemeriksaan.click()
                                page.wait_for_timeout(1000)

                                # Input Data Pemeriksaan Gizi Anak Sekolah
                                gizi_anak(page, row_excel, df_who)
                                tensi_siswa(page, row_excel)
                                gigi_siswa(page, row_excel)
                                mata_telinga_siswa(page, row_excel)
                                page.wait_for_timeout(4000)

                                selesai_pemeriksaan = page.locator("button:has(div.tracking-wide:has-text('Selesaikan Layanan'))")
                                selesai_pemeriksaan.click()
                                page.wait_for_timeout(2000)

                                hadir_btn = page.locator("button:has(div.tracking-wide:has-text('Konfirmasi'))").last
                                hadir_btn.click()

                print("🔄 Semua kelas sudah diproses, kembali ke menu awal...")
            except Exception as e:
                print(f"⚠️ Error: {e}, ulang dari menu awal...")




if __name__ == "__main__":
    pelayanan()