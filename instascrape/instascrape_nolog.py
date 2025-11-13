#!/usr/bin/env python3
# coding: utf-8
"""
insta_public_search.py
- Gunakan Instaloader TANPA login untuk akun publik
- Mencari phrase di caption semua postingan (atau sampai max_posts)
- Menyimpan hasil (url, caption, tanggal) ke CSV
- Menambahkan delay dan exponential backoff bila terjadi error 401/403
Requirements:
    pip install instaloader pandas requests
Usage:
    python insta_public_search.py
"""

import instaloader
import time
import random
import pandas as pd
from datetime import datetime
import sys

# ---------- Konfigurasi ----------
TARGET = input("Masukkan username target (mis. valjubel): ").strip()
PHRASE = input("Masukkan kata / phrase yang dicari (mis. champion 2021): ").strip()
if not TARGET or not PHRASE:
    print("Target dan phrase harus diisi. Keluar.")
    sys.exit(1)

PHRASE_LOWER = PHRASE.lower()
DELAY_SECONDS = 3               # jeda normal antar postingan (atur 2-6 s)
MAX_POSTS = None                # batasi jumlah postingan (None = semua)
CSV_TEMPLATE = "hasil_public_{target}_{ts}.csv"
MAX_BACKOFF_TRIES = 6           # percobaan ulang ketika 401/403, dsb.

# (Opsional) proxy dict jika mau pakai proxy, contoh:
# PROXIES = {"http": "http://user:pass@host:port", "https": "http://user:pass@host:port"}
PROXIES = None  # set ke dict di atas jika perlu

# ---------- Inisialisasi Instaloader tanpa login ----------
L = instaloader.Instaloader(dirname_pattern=None,
                            download_pictures=False,
                            download_videos=False,
                            download_video_thumbnails=False,
                            save_metadata=False,
                            compress_json=False)

# Atur headers user-agent dan proxies di session requests internal Instaloader
ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
try:
    sess = L.context._session  # requests.Session used internally
    sess.headers.update({
        "User-Agent": ua,
        "Referer": "https://www.instagram.com/",
        "Accept-Language": "en-US,en;q=0.9",
    })
    if PROXIES:
        sess.proxies.update(PROXIES)
except Exception:
    # Jangan hentikan jika internal berubah; tetap coba tanpa kustomisasi
    pass

# ---------- Helper: backoff retry wrapper ----------
def with_backoff(fn, max_tries=MAX_BACKOFF_TRIES, base_delay=5):
    """
    Jalankan fn() dan jika mengecualikan HTTP 401/403 atau pesan 'Please wait a few minutes'
    lakukan exponential backoff dan retry hingga max_tries.
    """
    attempt = 0
    while True:
        try:
            return fn()
        except Exception as e:
            attempt += 1
            msg = str(e).lower()
            is_rate = ("401" in msg) or ("403" in msg) or ("please wait a few minutes" in msg) or ("graphql" in msg)
            if attempt >= max_tries or not is_rate:
                # jika bukan jenis rate-limit atau sudah habis coba, raise
                raise
            delay = base_delay * (2 ** (attempt - 1)) + random.random() * 3
            print(f"[!] Detected possible rate-limit or graphQL block (attempt {attempt}/{max_tries}).")
            print(f"    Error: {type(e).__name__}: {e}")
            print(f"    Menunggu {int(delay)} detik sebelum retry...")
            time.sleep(delay)
            continue

# ---------- Ambil profil target (dengan backoff jika perlu) ----------
try:
    def get_profile():
        return instaloader.Profile.from_username(L.context, TARGET)
    profile = with_backoff(get_profile)
except Exception as e:
    print("Gagal mengambil profil target. Pesan error:", type(e).__name__, e)
    print("Kemungkinan Instagram memblokir akses tanpa login atau akun tidak ada.")
    sys.exit(1)

print(f"Profil ditemukan: @{profile.username} — followers: {profile.followers}, posts: {profile.mediacount}")

# ---------- Iterasi postingan dan pencarian phrase ----------
results = []
count = 0

try:
    posts = profile.get_posts()
    for i, post in enumerate(posts):
        if MAX_POSTS and i >= MAX_POSTS:
            break
        count += 1

        # ambil caption dengan backoff kecil — kadang akses post detail memicu graphql
        def get_post_caption():
            # post.caption property memanggil metadata dari instagram
            return post.caption or ""
        try:
            caption = with_backoff(get_post_caption)
        except Exception as e:
            print(f"[!] Gagal ambil caption untuk post ke-{i+1}: {e}")
            # skip post ini dan lanjut; jangan keluar supaya dapat hasil sebagian
            caption = ""

        if PHRASE_LOWER in caption.lower():
            results.append({
                "url": post.url,
                "caption": caption,
                "date_utc": post.date_utc.isoformat(),
                "shortcode": post.shortcode
            })
            print(f"[+] Ditemukan di post #{i+1}: {post.url}")

        # delay random sedikit untuk meniru perilaku manusia
        sleep_time = DELAY_SECONDS + random.random() * 1.5
        time.sleep(sleep_time)

except KeyboardInterrupt:
    print("\n[Dihentikan oleh user]")

except Exception as e:
    print("Terjadi error saat iterasi postingan:", type(e).__name__, e)
    print("Saran: tingkatkan DELAY_SECONDS, gunakan proxy, atau coba dengan akun login.")

# ---------- Simpan hasil ke CSV ----------
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_name = CSV_TEMPLATE.format(target=TARGET, ts=ts)
df = pd.DataFrame(results)
df.to_csv(csv_name, index=False, encoding="utf-8-sig")
print(f"\nSelesai. Total post diperiksa: {count}. Post cocok: {len(results)}.")
print("Hasil disimpan ke:", csv_name)

if len(results) == 0:
    print("Jika tidak ada hasil, pertimbangkan:")
    print(" - Cek manual apakah phrase memang ada di caption publik")
    print(" - Tingkatkan MAX_POSTS jika dibatasi")
    print(" - Tingkatkan DELAY_SECONDS untuk mengurangi blokir")
    print(" - Jika masih sering 401/403, pertimbangkan login atau Selenium/proxy.")
