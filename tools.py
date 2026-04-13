import asyncio
import os
from playwright.async_api import async_playwright

# Cấu hình
SAVE_PATH = "D:/TOOLS/outputs"
PROMPT_FILE = "D:/TOOLS/prompts.txt"

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

async def process_video(browser, prompt, index):
    # Mở tab mới
    page = await browser.contexts[0].new_page()
    
    try:
        print(f"\n🚀 [Video {index}] Đang chuẩn bị: {prompt[:30]}...")
        await page.goto("https://grok.com/imagine")
        
        # 1. Chọn chế độ Video
        print(f"🎬 [Video {index}] Đang chuyển sang chế độ Video...")
        video_btn = page.locator('button:has(span:text-is("Video"))')
        await video_btn.wait_for(state="visible", timeout=20000)
        await video_btn.click()
        await asyncio.sleep(1) # Chờ menu options hiện ra

        # 2. Chọn thời lượng 10s
        print(f"⏱️ [Video {index}] Đang chọn thời lượng 10s...")
        try:
            # Tìm button chứa chính xác text 10s
            duration_btn = page.locator('button:has(span:text-is("10s"))')
            await duration_btn.click()
        except Exception as e:
            print(f"⚠️ Không chọn được 10s: {e}")

        # 3. Chọn tỷ lệ khung hình 9:16
        print(f"📱 [Video {index}] Đang chỉnh tỷ lệ 9:16...")
        try:
            # Click vào nút dropdown Tỷ lệ khung hình
            ratio_dropdown = page.locator('button[aria-label*="khung hình"]')
            await ratio_dropdown.click()
            await asyncio.sleep(0.5)
            
            # Chọn option 9:16 trong menu vừa hiện
            ratio_916_btn = page.locator('button:has(span:text-is("9:16"))')
            await ratio_916_btn.click()
        except Exception as e:
            print(f"⚠️ Không chỉnh được tỷ lệ 9:16: {e}")

        # 4. Nhập prompt
        # Grok dùng div contenteditable thay vì textarea thông thường
        input_selector = 'div[contenteditable="true"]'
        await page.wait_for_selector(input_selector)
        
        print(f"📝 [Video {index}] Đang dán prompt...")
        await page.fill(input_selector, prompt) 
        
        # 5. Nhấn Enter để gửi lệnh tạo
        print(f"📤 [Video {index}] Đang gửi lệnh tạo video...")
        await page.keyboard.press("Enter")
        
        # Đợi 15 giây để quan sát xem Grok đã bắt đầu render chưa
        await asyncio.sleep(15)
        print(f"✅ [Video {index}] Đã gửi xong! Tab sẽ giữ nguyên để render.")

    except Exception as e:
        print(f"❌ [Video {index}] Lỗi: {e}")
    # Bạn có thể đóng page sau khi gửi xong, nhưng tôi khuyên nên giữ để xem tiến trình
    # await page.close() 

async def main():
    if not os.path.exists(PROMPT_FILE):
        print(f"❌ Không tìm thấy file {PROMPT_FILE}!")
        return

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        all_prompts = [line.strip() for line in f if line.strip()]

    async with async_playwright() as p:
        try:
            # Kết nối vào Chrome đang mở sẵn (port 9222)
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print(f"--- Đã kết nối Chrome Debug. Tổng số prompt: {len(all_prompts)} ---")

            # Chạy tuần tự để đảm bảo các bước click chọn option (10s, 9:16) chuẩn xác
            for i, pmt in enumerate(all_prompts):
                await process_video(browser, pmt, i+1)

            print("\n🎉 TẤT CẢ LỆNH ĐÃ ĐƯỢC GỬI THÀNH CÔNG!")

        except Exception as e:
            print(f"Lỗi kết nối: {e}")

if __name__ == "__main__":
    asyncio.run(main())