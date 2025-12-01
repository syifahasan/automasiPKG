import time
from datetime import datetime
import re
from playwright.sync_api import sync_playwright
import random
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

def skriningMandiri(page,jk,umur):
    def demografi_dewasa():
        if umur >=17 and umur <60:
            page.locator(f"tr.border-b-solid:has-text('Demografi Dewasa {jk}') >> text=Input Data").click()
            page.wait_for_timeout(1000)
            try:
                #Status Pernikahan
                belum_menikah = "sq_100i_0"
                sudah_menikah = "sq_100i_1"
                cerai_mati = "sq_100i_2"
                if umur >= 61 and umur <=100:
                    page.locator(f"input[type='radio']#{sudah_menikah}").check(force=True)
                elif umur > 22 and umur <= 60:
                    page.locator(f"input[type='radio']#{sudah_menikah}").check(force=True)
                else:
                    page.locator(f"input[type='radio']#{belum_menikah}").check(force=True)
                
                #Rencana Menikah
                page.locator(f"input[type='radio']#sq_101i_1").check(force=True)

                #Disabilitas / Status Hamil
                status_hamil = page.locator("div.sd-element:has-text('Apakah Anda sedang hamil?')")
                if status_hamil.count() > 0:
                    print("🟢 Pertanyaan status hamil ditemukan, mengisi jawaban...")
                    page.locator(f"input[type='radio']#sq_102i_1").check(force=True)

                    page.locator(f"input[type='radio']#sq_103i_0").check(force=True)
                else:
                    page.locator(f"input[type='radio']#sq_102i_0").check(force=True)

                
                page.locator(f"input[title='Kirim']").click()
                page.wait_for_timeout(3000)
            
            except Exception as e:
                print(f"⚠️ Terjadi kesalahan saat mengisi demografi: {e}")
        elif umur >=60:
            page.locator("tr.border-b-solid:has-text('Demografi Lansia') >> text=Input Data").click()
            page.wait_for_timeout(1000)
            try:
                #Status Pernikahan
                belum_menikah = "sq_100i_0"
                sudah_menikah = "sq_100i_1"
                cerai_mati = "sq_100i_2"
                page.locator(f"input[type='radio']#{sudah_menikah}").check(force=True)

                #status disabilitas
                page.locator(f"input[type='radio']#sq_101i_0").check(force=True)

                page.locator(f"input[title='Kirim']").click()
                page.wait_for_timeout(3000)
            
            except Exception as e:
                print(f"⚠️ Terjadi kesalahan saat mengisi demografi: {e}")
    
    def skrining_hati():
        page.locator("tr.border-b-solid:has-text('Hati') >> text=Input Data").click()
        page.wait_for_timeout(1000)
        try:
            # Apakah Anda pernah menjalani tes untuk Hepatitis B dan mendapatkan hasil positif?
            page.locator(f"input[type='radio']#sq_100i_1").check(force=True)

            # Apakah Anda memiliki ibu kandung/saudara sekandung yang menderita Hepatitis B?
            page.locator(f"input[type='radio']#sq_101i_1").check(force=True)

            # Apakah Anda pernah melakukan hubungan intim / seksual dengan orang yang bukan pasangan resmi Anda?
            page.locator(f"input[type='radio']#sq_102i_1").check(force=True)

            #Apakah Anda pernah menerima transfusi darah sebelumnya?
            page.locator(f"input[type='radio']#sq_103i_1").check(force=True)

            #Apakah Anda pernah menjalani cuci darah  atau hemodialisis?
            page.locator(f"input[type='radio']#sq_104i_1").check(force=True)

            # Apakah Anda pernah menggunakan narkoba, obat terlarang, atau bahan adiktif lainnya dengan cara disuntik?
            page.locator(f"input[type='radio']#sq_105i_1").check(force=True)

            # Apakah Anda adalah orang dengan HIV (ODHIV)?
            page.locator(f"input[type='radio']#sq_106i_1").check(force=True)

            # Apakah Anda pernah mendapatkan pengobatan Hepatitis C dan tidak sembuh?
            page.locator(f"input[type='radio']#sq_107i_1").check(force=True)

            # Apakah Anda pernah didiagnosa atau mendapatkan hasil pemeriksaan kolesterol (lemak darah) tinggi?
            page.locator(f"input[type='radio']#sq_108i_1").check(force=True)

            
            page.locator(f"input[title='Kirim']").click()
            page.wait_for_timeout(3000)
        
        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi skrining hati: {e}")

    def kanker_usus():
        try:
            if page.locator("tr.border-b-solid:has-text('Kanker Usus') >> text=Input Data").count() == 0:
                print("ℹ️ Kanker Usus tidak tersedia untuk pasien ini, skip...")
                return
            
            page.locator("tr.border-b-solid:has-text('Kanker Usus') >> text=Input Data").click()
            page.wait_for_timeout(1000)

            page.locator(f"input[type='radio']#sq_100i_1").check(force=True)
            page.locator("#sq_101i").click()
            if jk == "Laki-Laki":
                page.locator(f"div[title='Ya']").click()
            else:
                page.locator(f"div[title='Tidak']").click()
            
            page.locator(f"input[title='Kirim']").click()
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi kanker usus: {e}")
    
    def skrining_jiwa():
        page.locator("tr.border-b-solid:has-text('Kesehatan Jiwa') >> text=Input Data").click()
        page.wait_for_timeout(1000)

        try:
            # Dalam 2 minggu terakhir, seberapa sering anda kurang/ tidak bersemangat dalam melakukan kegiatan sehari-hari?
            if umur >=60:
                page.locator(f"input[type='radio']#sq_100i_1").check(force=True)
            else:
                page.locator(f"input[type='radio']#sq_100i_0").check(force=True)

            # Dalam 2 minggu terakhir, seberapa sering anda merasa murung, tertekan, atau putus asa?
            page.locator(f"input[type='radio']#sq_101i_0").check(force=True)

            # Dalam 2 minggu terakhir,  seberapa sering anda merasa gugup, cemas, atau gelisah?
            page.locator(f"input[type='radio']#sq_102i_0").check(force=True)

            # Dalam 2 minggu terakhir,  seberapa sering anda tidak mampu mengendalikan rasa khawatir?
            page.locator(f"input[type='radio']#sq_103i_0").check(force=True)
            
            page.locator(f"input[title='Kirim']").click()
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi skrining jiwa: {e}")

    def perilaku_merokok():
        page.locator("tr.border-b-solid:has-text('Perilaku Merokok') >> text=Input Data").click()
        page.wait_for_timeout(1000)
        try:
            status_ya = "0"
            status_tidak = "1"
            # Apakah Anda merokok dalam setahun terakhir ini?
            if jk == "Laki-Laki" and 20 <= umur < 25: 
                page.locator(f"input[type='radio']#sq_100i_{status_tidak}").check(force=True)

                page.wait_for_timeout(2000)
            else:
                page.locator(f"input[type='radio']#sq_100i_{status_tidak}").check(force=True)
                page.wait_for_timeout(2000)
            
            #
            if page.locator("div#sq104").count() == 0:
                if jk == "Laki-Laki" and 20 <= umur < 25:
                    page.locator(f"input[type='radio']#sq_107i_{status_ya}").check(force=True)
                else:
                    page.locator(f"input[type='radio']#sq_107i_{status_tidak}").check(force=True)
            if jk == "Laki-Laki" and 20 <= umur < 25: 
                page.locator(f"input[type='radio']#sq_104i_{status_ya}").check(force=True)
            else:
                page.locator(f"input[type='radio']#sq_104i_{status_tidak}").check(force=True)
            
            
            page.locator(f"input[title='Kirim']").click()
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi perilaku merokok: {e}")

    def gula_tensi():
        try:
            if page.locator("tr.border-b-solid:has-text('Tekanan Darah & Gula Darah') >> text=Input Data").count() == 0:
                print("ℹ️ Kanker Usus tidak tersedia untuk pasien ini, skip...")
                return

            page.locator("tr.border-b-solid:has-text('Tekanan Darah & Gula Darah') >> text=Input Data").click()
            page.wait_for_timeout(1000)

            #  Apakah Anda pernah dinyatakan tekanan darah tinggi?
            page.locator(f"input[type='radio']#sq_100i_1").check(force=True)

            # Apakah Anda pernah dinyatakan diabetes atau kencing manis?
            page.locator(f"input[type='radio']#sq_101i_1").check(force=True)

            
            page.locator(f"input[title='Kirim']").click()
            page.wait_for_timeout(3000)

        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi skrining tensi dan gula: {e}")

    def kanker_paru():
        try:
            if page.locator(f"tr.border-b-solid:has-text('Skrining Kanker Paru ({jk} >=45 Tahun) - Penapisan Risiko') >> text=Input Data").count() == 0:
                print("ℹ️ Kanker Usus tidak tersedia untuk pasien ini, skip...")
                page.wait_for_timeout(2000)
                return
            
            page.locator(f"tr.border-b-solid:has-text('Skrining Kanker Paru ({jk} >=45 Tahun) - Penapisan Risiko') >> text=Input Data").click()
            page.wait_for_timeout(1000)

            # Apakah Anda merokok dalam setahun terakhir ini?
            page.locator(f"input[type='radio']#sq_100i_1").check(force=True)
            page.wait_for_timeout(2000)

            # Apakah Anda pernah memiliki riwayat merokok dalam 15 tahun terakhir?
            page.locator(f"input[type='radio']#sq_101i_0").check(force=True)

            # Apakah Anda terpapar asap rokok atau menghirup asap rokok dari orang lain dalam sebulan terakhir?
            page.locator(f"input[type='radio']#sq_102i_0").check(force=True)

            # Apakah memiliki riwayat kanker paru pada keluarga (ayah/ibu/saudara kandung)?
            page.locator(f"input[type='radio']#sq_103i_1").check(force=True)

            
            page.locator(f"input[title='Kirim']").click()
            page.wait_for_timeout(3000)
        
        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi kanker paru: {e}")
    
    def aktivitas_fisik():
        try:
            if page.locator("tr.border-b-solid:has-text('Tingkat Aktivitas Fisik') >> text=Input Data").count() == 0:
                print("ℹ️ Aktivitas Fisik tidak tersedia untuk pasien ini, skip...")
                return
            
            page.locator("tr.border-b-solid:has-text('Aktivitas Fisik') >> text=Input Data").click()
            page.wait_for_timeout(1000)

            #  Apakah Anda rutin melakukan olahraga, (seperti jalan cepat, lari, bersepeda, senam, berenang, bulutangkis, sepakbola atau olahraga lainnya)?
            if umur >=18 and umur <30:
                page.locator(f"input[type='radio']#sq_100i_0").check(force=True)
                page.wait_for_timeout(1000)

                # Dalam seminggu terakhir, berapa kali Anda berolahraga?
                page.fill("#sq_101i", "2")

                # Berapa menit biasanya anda melakukan olahraga tersebut setiap satu kali olahraga?
                page.fill("#sq_102i", "30")
            else:
                page.locator(f"input[type='radio']#sq_100i_1").check(force=True)

            
            page.locator(f"input[title='Kirim']").click()
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi aktivitas fisik: {e}")

    def tuberkulosis():
        try:
            if page.locator("tr.border-b-solid:has-text('Tuberkulosis') >> text=Input Data").count() == 0:
                print("ℹ️ Skrining Tuberkulosis tidak tersedia untuk pasien ini, skip...")
                page.wait_for_timeout(2000)
                return
            
            page.locator("tr.border-b-solid:has-text('Tuberkulosis') >> text=Input Data").click()
            page.wait_for_timeout(1000)

            #  Apakah Anda pernah atau sedang mengalami batuk yang tidak sembuh-sembuh selama lebih dari 2 minggu?
            page.locator(f"input[type='radio']#sq_100i_1").check(force=True)

            # Apakah Anda tinggal serumah atau sering bertemu dengan orang yang menderita Tuberkulosis (TBC) atau batuk berkepanjangan?
            page.locator(f"input[type='radio']#sq_101i_1").check(force=True)

            
            page.locator(f"input[title='Kirim']").click()
            page.wait_for_timeout(3000)

        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi tuberkulosis: {e}")

     
    demografi_dewasa()
    skrining_hati()
    kanker_usus()
    skrining_jiwa()
    perilaku_merokok()
    gula_tensi()
    kanker_paru()
    aktivitas_fisik()
    tuberkulosis()

def pelayananNakes(page, jk, umur):

    def generate_bb_tb():
        jk_l = jk.lower()

        if 18 <= umur < 60:
            if jk_l == "laki-laki":
                bb = random.randint(60, 80)
                tb = random.randint(165, 175)
            else:
                bb = random.randint(50, 70)
                tb = random.randint(155, 170)

        elif umur >= 60:
            if jk_l == "laki-laki":
                bb = random.randint(55, 75)
                tb = random.randint(160, 170)
            else:
                bb = random.randint(45, 65)
                tb = random.randint(150, 165)

        return bb, tb
    

    def generate_lingkar_perut(tb):
        base = tb * 0.45

        if jk.lower() == "laki-laki":
            return int(base + random.randint(-8, 12))
        else:
            return int(base + random.randint(-6, 10))
    

    def generate_tensi():
        if umur < 40:
            if jk.lower() == "laki-laki":
                systolic = random.randint(120, 130)
                diastolic = random.randint(75, 85)
            else:
                systolic = random.randint(110, 130)
                diastolic = random.randint(70, 85)
        else:
            systolic = random.randint(120, 150)
            diastolic = random.randint(80, 95)

        return systolic, diastolic
    

    def gula_darah():
        try:
            page.locator("div.flex.items-center:has-text('Skrining Gula Darah') >> text=Input Data").click()
            page.wait_for_timeout(3000)

            gula = random.randint(90, 140)
            print(f"🔢 Randomized Gula Darah → {gula} mg/dL")

            page.fill("#sq_100i", str(gula))
            page.locator("input[title='Kirim']").click()
            page.wait_for_timeout(3000)

        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi gula darah: {e}")

        
    def bb_tb():
        try:
            page.locator(f"div.flex.items-center:has-text('Gizi (BB - TB - Lingkar Perut) {jk}') >> text=Input Data").click()
            page.wait_for_timeout(3000)

            bb, tb = generate_bb_tb()
            lp = generate_lingkar_perut(tb)

            print(f"🔢 Randomized BB/TB → BB: {bb} kg | TB: {tb} cm | LP: {lp}")

            page.fill("#sq_100i", str(bb))
            page.fill("#sq_101i", str(tb))
            page.fill("#sq_102i", str(lp))

            page.locator("input[title='Kirim']").click()
            page.wait_for_timeout(3000)

        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi BB dan TB: {e}")


    def tensi():
        try:
            page.locator("div.flex.items-center:has-text('Pemeriksaan Tekanan Darah') >> text=Input Data").click()
            page.wait_for_timeout(3000)

            systolic, diastolic = generate_tensi()
            print(f"🔢 Randomized Tensi → Sistolik: {systolic} mmHg | Diastolik: {diastolic} mmHg")

            page.fill("#sq_100i", str(systolic))
            page.fill("#sq_101i", str(diastolic))

            page.locator("input[title='Kirim']").click()
            page.wait_for_timeout(3000)

        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengisi tensi: {e}")


    # Jalankan semua pemeriksaan
    bb_tb()
    tensi()
    gula_darah()

            

def pelayananumum():
    profile_path = r"E:\ChromeProfileAutomation"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            r"E:\ChromeProfileAutomation",
            channel="chrome",
            headless=False,
            args=[
                "--disable-session-crashed-bubble",
                "--disable-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ]
        )
        today = datetime.today()
        hari = today.day
        bulan = today.strftime("%b")
        bulan_full = today.strftime("%B")
        header_bulan = today.strftime("%b %Y")
        tanggal_str = today.strftime("%Y-%m-%d")

        page = browser.new_page()
        page.goto("https://sehatindonesiaku.kemkes.go.id", wait_until="load")
        
        while True:
            page.click("section.fixed >> text='CKG Umum'")
            page.click("text='Pelayanan'")
            page.wait_for_timeout(300)

            page.locator("div.ml-4").click()
            page.wait_for_timeout(400)

            print(f"📅 Memilih tanggal pemeriksaan: {hari} {header_bulan} {today.year}")

            selector_tanggal = f"td.cell[title='{tanggal_str}']"
            page.locator(selector_tanggal).first.click()
            page.wait_for_timeout(200)
            page.locator(selector_tanggal).first.click()
            page.wait_for_timeout(300)


            try:
                modal_locator = page.locator("text=Pengaturan Pelayanan")
                modal_locator.wait_for(state="visible", timeout=5000)

                print("🟢 Modal Pengaturan Pelayanan terdeteksi, klik tombol Simpan...")
                page.get_by_role("button", name="Simpan").click()
                print("✅ Tombol Simpan diklik.")

            except PlaywrightTimeoutError:
                print("ℹ️ Modal Pengaturan Pelayanan tidak muncul, lanjut ke proses berikutnya.")
                

            buttons = page.locator("ul >> li")
            last_page_text = buttons.nth(-2).inner_text()

            if last_page_text.isdigit():
                total_halaman = int(last_page_text)
            else:
                # fallback: cari angka terbesar dari semua tombol
                texts = [b.inner_text() for b in buttons.all()]
                angka = [int(t) for t in texts if t.isdigit()]
                total_halaman = max(angka)

            print(f"📑 Total halaman: {total_halaman}")

            ada_belum = False

            for h in range(total_halaman):
                print(f"➡ Proses halaman {h+1} dari {total_halaman}")

                belum_diperiksa_rows = page.locator("div:has-text('Belum Pemeriksaan')")

                
                belum_diperiksa_locators = page.get_by_text("Belum Pemeriksaan")
                count = belum_diperiksa_locators.count()

                if count > 0:
                    print(f"    🔘 Ditemukan {count} peserta belum di periksa")
                    rows = page.locator("table tbody tr")

                    for i in range(rows.count()):
                        row = rows.nth(i)
                        status = row.locator("td").filter(has_text="Belum Pemeriksaan")
                        if status.count() > 0:
                            ada_belum = True
                            tombol_mulai = row.locator("button:has(div.tracking-wide:has-text('Mulai'))")
                            if tombol_mulai.count() > 0:
                                tombol_mulai.first.click()
                                page.wait_for_timeout(1500)
                                # umur_text = page.locator("text=Tahun").nth(0).inner_text()
                                # jenis_kelamin = page.locator("text=Laki-Laki, Perempuan").first.inner_text()

                                jenis_kelamin = page.locator(
                                    "//div[contains(text(), 'Jenis Kelamin')]/following-sibling::div"
                                ).inner_text()
                                print("Jenis Kelamin:", jenis_kelamin)

                                umur = page.locator(
                                    "//div[contains(text(), 'Umur')]/following-sibling::div"
                                ).inner_text()
                                print("Umur:", umur)

                                umur_tahun = int(re.search(r"(\d+)\s*Tahun", umur).group(1))

                                print(f"👤 Umur: {umur_tahun} tahun | Jenis Kelamin: {jenis_kelamin}")

                                skriningMandiri(page, jenis_kelamin, umur_tahun)
                                btn_selesai = page.locator("button:has(div.tracking-wide:has-text('Selesaikan Layanan'))")
                                btn_mulai = page.locator("button:has(div.tracking-wide:has-text('Mulai Pemeriksaan'))")
                                if btn_mulai.is_visible():
                                    print("🔘 Tombol 'Mulai Pemeriksaan' ditemukan → klik dulu")
                                    btn_mulai.click()
                                    page.wait_for_timeout(1000)
                                    # page.wait_for_selector("text=Konfirmasi Tanggal Pemeriksaan").is_visible()
                                    # page.locator("button:has-text('Simpan')").click()
                                elif btn_selesai.is_visible():
                                    print("✅ Sudah di halaman pemeriksaan, tombol 'Selesaikan Layanan' tersedia → langsung isi form")
                                else:
                                    print("⚠️ Tidak ditemukan tombol pemeriksaan, skip peserta ini")
                                    continue
                                page.wait_for_timeout(1000)
                                pelayananNakes(page, jenis_kelamin, umur_tahun)
                                btn_selesai.click()
                                hadir_btn = page.locator("button:has(div.tracking-wide:has-text('Konfirmasi'))").last
                                hadir_btn.click()
                                page.wait_for_timeout(2000)
                                break

                if ada_belum:
                    break
                        
                else:
                    print("    ℹ️ Tidak ada peserta dengan status 'Belum Pemeriksaan' di halaman ini")

                
                if h < total_halaman - 1:
                            next_button = page.locator("ul.vpagination li.page-item a.page-link").last
                            next_button.click()
                            page.wait_for_timeout(2000)
            
            if not ada_belum:
                print("✅ Semua peserta telah diperiksa di semua halaman.")
                break

if __name__ == "__main__":
    pelayananumum()