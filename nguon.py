# import pandas as pd
# import asyncio
# import math
# from playwright.async_api import async_playwright
# import screeninfo

# # =================== CẤU HÌNH ===================
# FILE_PATH = r"C:\Users\TRUONG\Desktop\playwright\phone.xlsx"
# COMMON_PASSWORD = "env2025qis!!@@"

# FULLSCREEN_F11 = True        # Đổi thành False nếu không muốn F11
# DELAY_BEFORE_HOAT_DONG = 6   # Đợi 6 giây sau khi vào trang Lãnh đạo rồi mới click "Hoạt động"
# # ================================================

# async def main():
#     # Lấy độ phân giải màn hình
#     try:
#         monitor = screeninfo.get_monitors()[0]
#         SCREEN_WIDTH = monitor.width
#         SCREEN_HEIGHT = monitor.height
#         print(f"Phát hiện màn hình: {SCREEN_WIDTH} × {SCREEN_HEIGHT}")
#     except:
#         SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
#         print("Dùng mặc định 1920×1080")

#     df = pd.read_excel(FILE_PATH, dtype={'username': str}).dropna()
#     df.columns = df.columns.str.strip()
#     if len(df) == 0 or 'username' not in df.columns:
#         print("Không có tài khoản nào trong file Excel!")
#         return

#     total = len(df)
#     print(f"\nĐang mở {total} tài khoản – Tự động vào 'Hoạt động' sau {DELAY_BEFORE_HOAT_DONG} giây\n")

#     cols = math.ceil(math.sqrt(total))
#     rows = math.ceil(total / cols)
#     w = SCREEN_WIDTH // cols
#     h = SCREEN_HEIGHT // rows

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=False,
#             args=[
#                 "--disable-notifications",
#                 "--mute-audio",
#                 "--disable-infobars",
#                 "--no-first-run",
#                 "--start-maximized",
#             ]
#         )

#         contexts = []

#         try:
#             for idx, row in df.iterrows():
#                 phone = str(row['username']).strip()

#                 context = await browser.new_context(
#                     viewport=None,
#                     screen={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
#                 )
#                 page = await context.new_page()

#                 # Set vị trí + kích thước cửa sổ
#                 cdp = await context.new_cdp_session(page)
#                 window_id = (await cdp.send("Browser.getWindowForTarget"))["windowId"]
#                 await cdp.send("Browser.setWindowBounds", {
#                     "windowId": window_id,
#                     "bounds": {
#                         "left": (idx % cols) * w,
#                         "top": (idx // cols) * h,
#                         "width": w,
#                         "height": h,
#                         "windowState": "normal"
#                     }
#                 })

#                 await page.goto("https://web.enetviet.com", wait_until="domcontentloaded")

#                 # Đăng nhập
#                 await page.fill("#usename", phone)
#                 await page.fill("input[name='password']", COMMON_PASSWORD)
#                 await page.click("button:has-text('Đăng nhập')")

#                 try:
#                     await page.wait_for_selector("#logoutButton", timeout=10000)
#                     print(f"[{phone}] Đăng nhập thành công")
#                 except:
#                     print(f"[{phone}] Đang load...")

#                 await asyncio.sleep(2)

#                 # Vào Lãnh đạo Nhà trường
#                 try:
#                     await page.click("p:has-text('Lãnh đạo Nhà trường')", timeout=10000)
#                 except:
#                     pass

#                 try:
#                     await page.click("img[src*='role-icon-5-0.svg']", timeout=120000)
#                     print(f"[{phone}] Đã vào trang Lãnh đạo")
#                 except:
#                     print(f"[{phone}] Không thấy ảnh lãnh đạo")

#                 # ĐỢI RỒI TỰ ĐỘNG CLICK "HOẠT ĐỘNG"
#                 print(f"[{phone}] Đang đợi {DELAY_BEFORE_HOAT_DONG} giây trước khi vào Hoạt động...")
#                 await asyncio.sleep(DELAY_BEFORE_HOAT_DONG)

#                 clicked = False
#                 selectors = [
#                     "text=Hoạt động",                                           # Cách tốt nhất
#                     "//span[text()='Hoạt động']",                               # XPath chắc chắn
#                     ".MuiListItemText-primary:has-text('Hoạt động')",           # Class chuẩn
#                     "//div[contains(@class,'MuiListItemButton-root')]//span[text()='Hoạt động']"  # Siêu chắc
#                 ]

#                 for selector in selectors:
#                     try:
#                         await page.click(selector, timeout=8000)
#                         print(f"[{phone}] ĐÃ CLICK THÀNH CÔNG VÀO 'HOẠT ĐỘNG'")
#                         clicked = True
#                         break
#                     except:
#                         continue

#                 if not clicked:
#                     print(f"[{phone}] KHÔNG BẤM ĐƯỢC 'HOẠT ĐỘNG' – Menu chưa load xong hoặc bị ẩn")

#                 # Nhấn F11 full màn hình
#                 if FULLSCREEN_F11:
#                     await page.keyboard.press("F11")
#                     await asyncio.sleep(0.5)

#                 contexts.append(context)

#             print(f"\nHOÀN TẤT! Đã mở và vào mục 'Hoạt động' cho {total} tài khoản.")
#             print("→ Nhấn Ctrl + C để đóng tất cả.\n")

#             while True:
#                 await asyncio.sleep(3600)

#         except KeyboardInterrupt:
#             print("\nĐang đóng tất cả cửa sổ...")
#         finally:
#             for ctx in contexts:
#                 try: await ctx.close()
#                 except: pass
#             await browser.close()

# if __name__ == "__main__":
#     asyncio.run(main())