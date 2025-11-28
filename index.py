# auto_chrome_playwright.py
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Tạo context giống người thật (user-agent, viewport, ngôn ngữ...)
        browser = await p.chromium.launch(headless=False)  # đổi True nếu muốn ẩn
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh",
            permissions=["geolocation"],
        )

        # Bỏ cái thông báo "Chrome is being controlled by automated software"
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """)

        page = await context.new_page()
        await page.goto("https://www.google.com")

        # Ví dụ: search tự động
        await page.fill('textarea[name="q"]', "web enetviet")
        await page.press('textarea[name="q"]', "Enter")
        await page.wait_for_timeout(3000)

        # Chụp màn hình
        await page.screenshot(path="google_search.png", full_page=True)

        await browser.close()

asyncio.run(main())