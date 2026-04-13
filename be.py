import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

# --- FIX LỖI NotImplementedError TRÊN WINDOWS ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Cấu hình đường dẫn
QUEUE_FILE = "D:/TOOLS/queue.json"
SAVE_PATH = "D:/TOOLS/outputs"

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

async def process_prompt(browser, prompt_data):
    prompt = prompt_data['text']
    idx = prompt_data['id']
    page = await browser.contexts[0].new_page()
    
    try:
        print(f"\n🚀 [ID {idx}] Đang bắt đầu: {prompt[:50]}...")
        await page.goto("https://grok.com/imagine")
        
        # 1. Chọn chế độ Video
        video_btn = page.locator('button:has(span:text-is("Video"))')
        await video_btn.wait_for(state="visible", timeout=20000)
        await video_btn.click()
        await asyncio.sleep(2)

        # 2. Chỉnh 10s & 9:16
        try:
            await page.locator('button:has(span:text-is("10s"))').click()
            print(f"⏱️ [ID {idx}] Đã chọn 10s")
        except: pass
        
        try:
            await page.locator('button[aria-label*="khung hình"]').click()
            await asyncio.sleep(1)
            await page.locator('button:has(span:text-is("9:16"))').click()
            print(f"📱 [ID {idx}] Đã chọn 9:16")
        except: pass

        # 3. Nhập prompt & Gửi
        input_selector = 'div[contenteditable="true"]'
        await page.wait_for_selector(input_selector)
        await page.fill(input_selector, prompt)
        await page.keyboard.press("Enter")
        
        # 4. CHỜ RENDER XONG 100% VÀ TẢI XUỐNG
        print(f"⏳ [ID {idx}] Đang canh render 100%... (Có thể mất vài phút)")
        
        # Selector cho nút tải xuống (Bắt theo icon SVG tải xuống hoặc aria-label)
        download_btn_selector = 'button[aria-label*="Tải xuống"], button:has(svg[viewBox="0 0 20 20"])'
        
        # Đợi tối đa 10 phút (600.000ms) cho đến khi nút tải hiện ra
        download_btn = await page.wait_for_selector(download_btn_selector, state="visible", timeout=600000)
        
        # Thực hiện tải về
        file_name = f"video_{idx}.mp4"
        final_file_path = os.path.join(SAVE_PATH, file_name)
        
        async with page.expect_download() as download_info:
            await download_btn.click()
        
        download = await download_info.value
        await download.save_as(final_file_path)
        
        print(f"✅ [ID {idx}] HOÀN THÀNH: {final_file_path}")
        
    except Exception as e:
        print(f"❌ [ID {idx}] Gặp lỗi: {e}")
    finally:
        await page.close()

async def main():
    print("🛰️ BE Worker (Render & Download) đang chạy...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("--- Đã kết nối Chrome Debug thành công ---")
            
            while True:
                if os.path.exists(QUEUE_FILE):
                    try:
                        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                            queue = json.load(f)
                    except: queue = []
                    
                    if queue:
                        current_task = queue.pop(0)
                        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                            json.dump(queue, f, indent=4, ensure_ascii=False)
                        
                        # Xử lý tuần tự từng cái một
                        await process_prompt(browser, current_task)
                
                await asyncio.sleep(3) 
        except Exception as e:
            print(f"❌ Lỗi: {e}. Đảm bảo Chrome Debug port 9222 đang mở!")

if __name__ == "__main__":
    asyncio.run(main())