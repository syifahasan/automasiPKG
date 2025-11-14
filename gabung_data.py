import pandas as pd

# Baca kedua file (ubah baris header sesuai posisi aslinya)
df_tb = pd.read_excel("C:/Users/PKM_SJNT/Documents/PKGSEKOLAH/HASIL/SDN DADAP 1/SDN 1 DADAP_kelas 4.xlsx", header=7)   # header di baris ke-8
df_nik = pd.read_excel("C:/Users/PKM_SJNT/Documents/PKGSEKOLAH/HASIL/SDN DADAP 1/Tahun2025DataPuskesmasUPTDSDN1Dadap.xlsx", header=4)  # header di baris ke-5

# Normalisasi kolom nama (biar bisa dicocokkan)
df_nik["NamaKey"] = df_nik["Nama"].astype(str).str.strip().str.lower()
df_tb["NamaKey"] = df_tb["Nama"].astype(str).str.strip().str.lower()

# Buat dictionary: Nama → NIK
dict_nik = dict(zip(df_nik["NamaKey"], df_nik["NIK"]))

# Tambahkan kolom NIK ke df_tb berdasarkan NamaKey
df_tb["NIK"] = df_tb["NamaKey"].map(dict_nik)

# Simpan hasilnya
df_tb.to_excel("data_tb_bb_dengan_nik.xlsx", index=False)

print("✅ NIK berhasil ditambahkan ke data_tb_bb_dengan_nik.xlsx")
