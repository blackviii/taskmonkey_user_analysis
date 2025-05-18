import asyncio
from playwright.async_api import async_playwright

async def get_cookie():
    """
    访问特定 URL 获取 cookie
    
    返回:
        dict: 获取到的 cookie 字典
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 访问启用 API 的 URL
            await page.goto('https://api.taskmonkey.ai/api/index/enable/update?secret_key=tastAdmin77123')
            
            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')
            
            # 获取所有 cookie
            cookies = await context.cookies()
            
            # 转换成字典格式便于使用
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            return cookie_dict
        except Exception as e:
            print(f"获取 cookie 时出错: {e}")
            return {}
        finally:
            await browser.close()

# 使用同步方式调用异步函数
def get_cookie_sync():
    """同步方式获取 cookie"""
    cookie_dict = asyncio.run(get_cookie())
    return cookie_dict

if __name__ == "__main__":
    # 测试获取 cookie
    cookie_dict = get_cookie_sync()
    
    if cookie_dict:
        print("成功获取 Cookie:")
        for name, value in cookie_dict.items():
            print(f"{name}: {value}")
    else:
        print("获取 Cookie 失败") 