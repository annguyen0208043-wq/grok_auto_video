import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def run():
    async with async_playwright() as p:
        # Thêm các args để tắt dòng thông báo "automated test software"
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./grok_session",
            headless=False,
            channel="chrome",
            no_viewport=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        
        page = await context.new_page()
        
        # Kích hoạt chế độ tàng hình
        await stealth_async(page)
        
        # Thêm User-Agent thật của trình duyệt
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        await page.goto("https://grok.com/")
        
        print("\n" + "="*50)
        print("ĐÃ KÍCH HOẠT CHẾ ĐỘ TÀNG HÌNH.")
        print("Nếu vẫn hiện Cloudflare, hãy tự tay nhấn 'Verify' trên trình duyệt nhé.")
        print("="*50 + "\n")
        
        input("Sau khi đăng nhập và vào được Grok, hãy nhấn Enter tại đây...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(run())