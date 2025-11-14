import asyncio
from playwright.async_api import async_playwright
import csv
import time

async def cari_caption(username, keyword):
    print(f"Mencari kata '{keyword}' di akun @{username} ... (tanpa login)")

    hasil = []
    max_scroll = 30  # ubah sesuai kebutuhan

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = await context.new_page()

        try:
            await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            await page.wait_for_selector("article", timeout=20000)
        except Exception as e:
            print(f"Gagal membuka profil @{username}: {e}")
            await browser.close()
            return

        print("Berhasil membuka profil, mulai scroll...")

        last_height = await page.evaluate("document.body.scrollHeight")
        for i in range(max_scroll):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        posts = await page.query_selector_all("article a[href*='/p/']")
        print(f"Memeriksa {len(posts)} posting...")

        for post in posts:
            href = await post.get_attribute("href")
            post_url = f"https://www.instagram.com{href}"
            try:
                await page.goto(post_url, timeout=30000)
                await asyncio.sleep(1.5)
                caption_elem = await page.query_selector("h1, div[role='button'] span")
                caption_text = await caption_elem.inner_text() if caption_elem else ""
                if keyword.lower() in caption_text.lower():
                    hasil.append((caption_text[:100].replace("\n", " "), post_url))
                    print(f"✓ Ditemukan di {post_url}")
            except Exception:
                continue

        await browser.close()

    filename = f"hasil_pencarian_{username}_{int(time.time())}.csv"
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Caption", "Link"])
        writer.writerows(hasil)

    if hasil:
        print(f"\nDitemukan {len(hasil)} postingan cocok. Disimpan ke {filename}")
    else:
        print(f"\nTidak ditemukan postingan dengan kata '{keyword}'.")

if __name__ == "__main__":
    asyncio.run(cari_caption("valjubel", "champion 2021"))
