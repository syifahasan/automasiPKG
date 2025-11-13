import asyncio
from playwright.async_api import async_playwright
import csv
import time

async def cari_caption(username, keyword):
    print(f"Mencari kata '{keyword}' di akun @{username} ... (tanpa login)")

    hasil = []
    max_scroll = 30  # ubah sesuai jumlah posting yang diinginkan

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

        last_height = await page.evaluate("document.body.scrollHeight")
        for i in range(max_scroll):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        posts = await page.query_selector_all("article a")
        print(f"Memeriksa {len(posts)} posting...")

        for post in posts:
            href = await post.get_attribute("href")
            if not href or not href.startswith("/p/"):
                continue

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

    # simpan ke CSV
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
