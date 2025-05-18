import asyncio
from playwright.async_api import async_playwright
import os

async def get_page_content(url, cookies=None, save_to_file=None):
    """
    获取指定URL的页面内容
    
    参数:
        url: 要获取内容的URL
        cookies: cookie 字典
        save_to_file: 可选，保存内容到文件路径
    
    返回:
        str: 页面HTML内容
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # 如果提供了cookies，则设置它们
        if cookies:
            for name, value in cookies.items():
                await context.add_cookies([{
                    'name': name,
                    'value': value,
                    'domain': 'api.taskmonkey.ai',
                    'path': '/'
                }])
        
        page = await context.new_page()
        
        try:
            # 访问指定URL
            await page.goto(url)
            
            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')
            
            # 获取页面内容
            content = await page.content()
            
            # 如果提供了保存路径，则保存内容到文件
            if save_to_file:
                os.makedirs(os.path.dirname(save_to_file), exist_ok=True)
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return content
        except Exception as e:
            print(f"获取页面内容时出错: {e}")
            return ""
        finally:
            await browser.close()

# 同步方式调用异步函数
def get_page_content_sync(url, cookies=None, save_to_file=None):
    """同步方式获取页面内容"""
    return asyncio.run(get_page_content(url, cookies, save_to_file))

if __name__ == "__main__":
    # 测试获取页面内容
    from get_cookie import get_cookie_sync
    
    # 获取 cookie
    cookies = get_cookie_sync()
    
    # 测试 URL
    test_url = 'https://api.taskmonkey.ai/api/user/index?orderBy=id'
    
    # 获取页面内容并保存到文件
    save_path = os.path.join(os.path.dirname(__file__), 'downloaded_page', 'test_page.html')
    
    content = get_page_content_sync(test_url, cookies, save_path)
    
    if content:
        print(f"页面内容已获取并保存到: {save_path}")
        print(f"内容长度: {len(content)} 字符")
    else:
        print("获取页面内容失败") 