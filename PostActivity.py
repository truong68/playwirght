import pandas as pd
import asyncio
import math
import os
import random
from playwright.async_api import async_playwright
import screeninfo

# =================== CẤU HÌNH ===================
FILE_PATH = r"C:\Users\TRUONG\Desktop\playwright\phone.xlsx"
COMMON_PASSWORD = "env2025qis!!@@"
DELAY_BEFORE_HOAT_DONG = 5
# ================================================

async def main():
    try:
        monitor = screeninfo.get_monitors()[0]
        SCREEN_WIDTH = monitor.width
        SCREEN_HEIGHT = monitor.height
        print(f"Màn hình: {SCREEN_WIDTH} × {SCREEN_HEIGHT}")
    except:
        SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
        print("Dùng mặc định 1920×1080")

    df = pd.read_excel(FILE_PATH, dtype={'username': str, 'content': str}).dropna(subset=['username'])
    df.columns = df.columns.str.strip()

    if len(df) == 0 or 'username' not in df.columns:
        print("Không có tài khoản nào!")
        return

    total = len(df)
    print(f"\nĐang mở {total} tài khoản – Full ô, không viền, tự động vào Hoạt động + mở khung đăng bài\n")

    cols = math.ceil(math.sqrt(total))
    rows = math.ceil(total / cols)
    w = SCREEN_WIDTH // cols
    h = SCREEN_HEIGHT // rows

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-infobars",
                "--disable-notifications",
                "--mute-audio",
                "--no-first-run",
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ]
        )

        contexts = []

        try:
            for idx, row in df.iterrows():
                phone = str(row['username']).strip()
                content = str(row['content']).strip() if ('content' in row and pd.notna(row['content'])) else ""

                # ====================== CHỈ THAY TỪ ĐÂY ======================
                context = await browser.new_context(
                    viewport=None,  # tắt viewport cố định
                    screen={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36",
                )

                # Tạo page + dùng --app để loại bỏ hoàn toàn thanh tab/address bar
                page = await context.new_page()
                await page.goto("about:blank")

                # Dùng CDP để tạo cửa sổ thực sự full ô, không viền
                cdp = await context.new_cdp_session(page)
                await cdp.send("Page.enable")
                win = await cdp.send("Browser.getWindowForTarget")

                x_pos = (idx % cols) * w
                y_pos = (idx // cols) * h

                await cdp.send("Browser.setWindowBounds", {
                    "windowId": win["windowId"],
                    "bounds": {
                        "left": x_pos,
                        "top": y_pos,
                        "width": w,
                        "height": h,
                        "windowState": "normal"
                    }
                })

                # Biến cửa sổ thành "app mode" → không thanh tab, không address bar
                await page.evaluate('''() => {
                    window.chrome = window.chrome || {};
                    window.chrome.app = { isInstalled: true };
                }''')
                await page.goto("https://web.enetviet.com", wait_until="domcontentloaded")
                # ============================================================

                await page.fill("#usename", phone)
                await page.fill("input[name='password']", COMMON_PASSWORD)
                await page.click("button:has-text('Đăng nhập')")

                try:
                    await page.wait_for_selector("#logoutButton", timeout=15000)
                    print(f"[{phone}] Đăng nhập thành công")
                except:
                    print(f"[{phone}] Đăng nhập thất bại hoặc chậm")

                await asyncio.sleep(2)
                await asyncio.sleep(DELAY_BEFORE_HOAT_DONG)

                clicked_hoatdong = False
                for sel in [
                    "text=Hoạt động",
                    "//span[normalize-space()='Hoạt động']",
                    ".MuiListItemText-primary:has-text('Hoạt động')"
                ]:
                    try:
                        await page.click(sel, timeout=2000)
                        print(f"[{phone}] ĐÃ VÀO HOẠT ĐỘNG")
                        clicked_hoatdong = True
                        break
                    except:
                        continue

                if not clicked_hoatdong:
                    print(f"[{phone}] Không bấm được 'Hoạt động'")
                    contexts.append(context)
                    continue

                await asyncio.sleep(4)

                clicked_post = False
                post_selectors = [
                    "text=Hay chia sẻ hoạt động của bạn...",
                    "text=Hãy chia sẻ hoạt động của bạn...",
                    "div.MuiStack-root.bg-\\[#F5F5F5\\].h-11.rounded-\\[100px\\]",
                    "//div[contains(@class,'MuiStack-root') and contains(@class,'bg-[#F5F5F5]') and .//p[contains(text(),'chia sẻ hoạt động')]]",
                    ".css-j7qwjs"
                ]

                for sel in post_selectors:
                    try:
                        await page.eval_on_selector(sel, "el => el.scrollIntoViewIfNeeded()")
                        await page.click(sel, timeout=10000, force=True)
                        print(f"[{phone}] ĐÃ MỞ KHUNG ĐĂNG BÀI THÀNH CÔNG!")
                        clicked_post = True
                        break
                    except Exception as e:
                        continue

                if not clicked_post:
                    print(f"[{phone}] KHÔNG TÌM THẤY Ô ĐĂNG BÀI – có thể trang chưa load xong")

                print(f"[{phone}] Đang focus và gõ nội dung...")
                try:
                    await page.wait_for_selector('div[contenteditable="true"]', state="visible", timeout=8000)
                    await page.click('div[contenteditable="true"]', force=True)
                    await asyncio.sleep(0.5)
                    await page.click('div[contenteditable="true"]', force=True)

                    await page.keyboard.down('Control')
                    await page.keyboard.press('A')
                    await page.keyboard.up('Control')
                    await page.keyboard.press('Backspace')

                    if content and content != "nan":
                        await page.keyboard.type(content)
                        print(f"[{phone}] ĐÃ GÕ NỘI DUNG: {content[:50]}{'...' if len(content)>50 else ''}")
                    else:
                        print(f"[{phone}] Không có nội dung để gõ (cột content trống)")

                except:
                    print(f"[{phone}] Lỗi khi focus/gõ nội dung")

                print(f"[{phone}] Đang bấm icon khung tròn xanh...")
                try:
                    await page.wait_for_selector('div.rounded-full.w-10.h-10 svg', timeout=10000)
                    clicked = False
                    for sel in [
                        'div.rounded-full.w-10.h-10 svg circle[cx="5.125"]',
                        'div.MuiStack-root.cursor-pointer.rounded-full.w-10.h-10',
                        'div.w-10.h-10 svg[width="22"]'
                    ]:
                        try:
                            await page.eval_on_selector(sel, "el => el.scrollIntoViewIfNeeded()")
                            await asyncio.sleep(0.3)
                            await page.click(sel, timeout=8000, force=True)
                            print(f"[{phone}] ĐÃ BẤM ICON KHUNG TRÒN XANH!")
                            clicked = True
                            break
                        except:
                            continue
                    if not clicked:
                        print(f"[{phone}] Không bấm được icon khung tròn xanh")
                except Exception as e:
                    print(f"[{phone}] Lỗi icon khung: {e}")

                await asyncio.sleep(1.5)

                print(f"[{phone}] Đang upload ảnh và đăng bài...")
                try:
                    import os
                    import random
                    IMAGE_FOLDER = r"C:\Users\TRUONG\Desktop\playwright\anh"

                    if os.path.exists(IMAGE_FOLDER):
                        images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png','.jpg','.jpeg','.gif','.webp','.bmp','.svg'))]
                        if images:
                            chosen = random.choice(images)
                            img_path = os.path.join(IMAGE_FOLDER, chosen)

                            async with page.expect_file_chooser() as fc_info:
                                await page.click('p:has-text("Thêm ảnh mới")', timeout=8000)
                            file_chooser = await fc_info.value
                            await file_chooser.set_files(img_path)
                            print(f"[{phone}] ĐÃ UPLOAD ẢNH: {chosen}")
                            await asyncio.sleep(5)

                            await page.click("button:has-text('Đăng')", timeout=10000)
                            print(f"[{phone}] ĐÃ BẤM NÚT ĐĂNG – HOÀN TẤT ĐĂNG BÀI!")
                        else:
                            print(f"[{phone}] Thư mục anh trống!")
                    else:
                        print(f"[{phone}] Không tìm thấy thư mục anh!")

                except Exception as e:
                    print(f"[{phone}] Lỗi khi up ảnh hoặc đăng bài: {e}")

                contexts.append(context)

            print(f"\nHOÀN TẤT! Đã đăng bài thành công cho {total} tài khoản!")
            print("Giữ cửa sổ mở... Nhấn Ctrl+C để thoát.\n")

            while True:
                await asyncio.sleep(3600)

        except KeyboardInterrupt:
            print("\nĐang đóng tất cả...")
        finally:
            for ctx in contexts:
                try: await ctx.close()
                except: pass
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())