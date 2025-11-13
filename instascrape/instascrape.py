#!/usr/bin/env python3
# coding: utf-8
"""
insta_search_with_cookies.py
- Load session dari cookie browser (dicopy ke file cookies.json atau paste saat runtime)
- Jika cookie gagal, fallback ke login username/password (dengan loop 2FA)
- Cari kata pada caption semua postingan akun target
- Simpan hasil (url, caption, tanggal) ke CSV
Requirements:
    pip install instaloader pandas requests
Usage:
    python insta_search_with_cookies.py
"""

import instaloader
import requests
import pandas as pd
import time
import os
import json
import getpass
from datetime import datetime

COOKIE_JSON_FILE = "cookies.json"   # optional: kamu bisa buat file JSON berisi cookie
CSV_OUTPUT_TEMPLATE = "hasil_pencarian_{target}_{ts}.csv"
DELAY_SECONDS = 5  # delay antara request supaya tidak kena rate-limit

# --------------- Helper: Ambil cookie (file atau input) ---------------
def load_cookies_from_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Pastikan format dict dengan kunci csrftoken, sessionid, ds_user_id, mid, ig_did
    return data

def prompt_cookies_interactively():
    print("Masukkan cookie Instagram yang diperlukan (copy dari DevTools -> Application -> Cookies -> instagram.com)")
    print("Jika kosong, tekan Enter untuk skip dan gunakan login username/password.")
    cookies = {}
    keys = ["csrftoken", "sessionid", "ds_user_id", "mid", "ig_did"]
    any_filled = False
    for k in keys:
        v = input(f"{k}: ").strip()
        if v:
            cookies[k] = v
            any_filled = True
    return cookies if any_filled else None

# --------------- Helper: set session dari cookie dict ---------------
def install_session_into_instaloader(L: instaloader.Instaloader, username: str, cookie_dict: dict):
    """
    Buat requests.Session, set cookie untuk domain .instagram.com, assign ke L.context._session,
    dan set L.context.username.
    """
    s = requests.Session()
    # set user-agent typical browser
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "Origin": "https://www.instagram.com",
    })
    # set cookies on proper domain
    domain = ".instagram.com"
    for k, v in cookie_dict.items():
        # only set non-empty values
        if v:
            s.cookies.set(k, v, domain=domain, path="/")

    # assign session to instaloader context
    L.context._session = s
    # set username in context so instaloader treats as logged in user
    L.context.username = username

# --------------- Helper: coba test login ---------------
def test_instaloader_login(L: instaloader.Instaloader):
    try:
        ok = L.test_login()  # raises exceptions if not logged in / server error
        return ok
    except Exception as e:
        # bisa lebih spesifik, tapi tampilkan pesan singkat
        print("test_login failed:", type(e).__name__, str(e))
        return False

# --------------- Fallback login (username/password dengan 2FA loop) ---------------
def login_with_password(L: instaloader.Instaloader, username: str, password: str, session_file=None):
    """
    Login dengan username/password, menangani TwoFactorAuthRequiredException,
    lalu simpan session jika berhasil.
    """
    try:
        L.login(username, password)
        print("Login berhasil tanpa 2FA.")
    except instaloader.TwoFactorAuthRequiredException:
        # loop sampai memasukkan kode 2FA yang valid atau user membatalkan (Ctrl+C)
        while True:
            code = input("Masukkan kode 2FA dari aplikasi authenticator / SMS: ").strip()
            try:
                L.two_factor_login(code)
                print("Login berhasil dengan 2FA.")
                break
            except instaloader.BadCredentialsException:
                print("Kode 2FA salah atau expired. Silakan coba lagi.")
    # simpan session file jika diberikan nama
    if session_file:
        try:
            L.save_session_to_file(session_file)
            print(f"Session disimpan ke file: {session_file}")
        except Exception as e:
            print("Gagal menyimpan session:", e)

# --------------- Main flow ---------------
def main():
    print("=== Insta search using browser cookie or fallback login ===")
    target = input("Masukkan target username (contoh: valjubel): ").strip()
    if not target:
        print("Target tidak boleh kosong. Keluar.")
        return

    kata = input("Masukkan kata/phrase yang dicari (contoh: champion 2021): ").strip()
    if not kata:
        print("Kata pencarian tidak boleh kosong. Keluar.")
        return

    username_login = input("Masukkan username akunmu untuk session/login (biarkan kosong jika ingin pakai cookie tanpa username): ").strip()
    if username_login == "":
        username_login = None

    # coba load cookie dari file dulu
    cookies = load_cookies_from_file(COOKIE_JSON_FILE)
    if not cookies:
        cookies = prompt_cookies_interactively()

    L = instaloader.Instaloader(dirname_pattern=None, download_pictures=False,
                                download_video_thumbnails=False, download_videos=False,
                                save_metadata=False, compress_json=False)
    # Disable downloading media; kita hanya butuh metadata

    logged_in = False

    # Jika cookie tersedia dan username disediakan, coba gunakan cookie
    if cookies and username_login:
        print("Mencoba load session dari cookie...")
        try:
            install_session_into_instaloader(L, username_login, cookies)
            time.sleep(1)
            if test_instaloader_login(L):
                print("Session cookie valid. Login via cookie berhasil.")
                logged_in = True
            else:
                print("Session cookie TIDAK valid atau expired.")
        except Exception as e:
            print("Gagal menggunakan cookie:", type(e).__name__, e)

    # Jika belum logged in, fallback ke username/password login
    session_file_name = None
    if not logged_in:
        choice = input("Gunakan login username/password sebagai fallback? (y/n) [y]: ").strip().lower() or "y"
        if choice != "y":
            print("Tidak ada session valid. Keluar.")
            return
        if not username_login:
            username_login = input("Masukkan username akunmu: ").strip()
        password_login = getpass.getpass("Masukkan password akunmu (input tersembunyi): ")
        # optional session file name
        session_file_name = f"{username_login}_session"
        try:
            login_with_password(L, username_login, password_login, session_file=session_file_name)
            # setelah login dengan instaloader, L.context._session sudah diset secara internal
            if test_instaloader_login(L):
                logged_in = True
            else:
                print("Login dengan password tampak gagal.")
        except Exception as e:
            print("Error saat login dengan password:", type(e).__name__, e)

    if not logged_in:
        print("Gagal login. Pastikan cookie valid atau kredensial benar. Keluar.")
        return

    # Sekarang kita sudah logged in (entah via cookie atau login), ambil profil target
    try:
        profile = instaloader.Profile.from_username(L.context, target)
    except Exception as e:
        print("Gagal mengambil profil target:", type(e).__name__, e)
        return

    print(f"Mencari kata '{kata}' di akun @{target} ... (tekan Ctrl+C untuk hentikan lebih awal)")

    results = []
    kata_lower = kata.lower()

    # opsi: batasi scanning untuk percobaan (set to None or int)
    max_posts_to_scan = None  # contoh: 200 untuk uji; None untuk semua

    try:
        for i, post in enumerate(profile.get_posts()):
            if max_posts_to_scan and i >= max_posts_to_scan:
                break
            caption = post.caption or ""
            if kata_lower in caption.lower():
                # simpan url, caption, tanggal
                results.append({
                    "url": post.url,
                    "caption": caption,
                    "date_utc": post.date_utc.isoformat()
                })
                print(f"[+] Ditemukan: {post.url} (post ke-{i+1})")
            else:
                # (opsional) print progress singkat setiap 50 postingan
                if i % 50 == 0 and i != 0:
                    print(f"... sudah memeriksa {i} postingan ...")
            time.sleep(DELAY_SECONDS)
    except KeyboardInterrupt:
        print("\nDihentikan manual oleh user. Menyimpan hasil yang sudah dikumpulkan...")
    except Exception as e:
        print("Error saat iterasi postingan:", type(e).__name__, e)
        # apabila error terkait 401/403 muncul, beritahu user
        print("Jika muncul 401/403, pertimbangkan untuk:\n - Memperpanjang delay (DELAY_SECONDS)\n - Menggunakan cookie baru dari browser\n - Menjalankan script di jaringan/IP lain")
    # Simpan hasil
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = CSV_OUTPUT_TEMPLATE.format(target=target, ts=ts)
    if results:
        df = pd.DataFrame(results)
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"\nSelesai. Ditemukan {len(results)} postingan, disimpan ke: {csv_file}")
    else:
        # tetap buat file kosong agar konsisten
        df = pd.DataFrame(results)
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print("\nSelesai. Tidak ditemukan postingan yang cocok. File kosong dibuat:", csv_file)

if __name__ == "__main__":
    main()
