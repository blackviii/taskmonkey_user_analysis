import asyncio
import re
import math
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from get_users_array_from_page import extract_total_users

async def get_page_total(cookies=None):
    """
    获取用户列表总页数
    
    参数:
        cookies: cookie 字典
    
    返回:
        int: 总页数
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
            # 访问用户列表页面
            await page.goto('https://api.taskmonkey.ai/api/user/index?orderBy=id')
            
            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')
            
            # 获取页面内容
            content = await page.content()
            
            # 提取用户总数并计算页数
            total_users = extract_total_users(content)
            
            # 一页显示10条记录，计算总页数
            page_total = math.ceil(total_users / 10)
            
            return page_total, total_users
        except Exception as e:
            print(f"获取总页数时出错: {e}")
            return 0, 0
        finally:
            await browser.close()

# 同步方式调用异步函数
def get_page_total_sync(cookies=None):
    """同步方式获取总页数"""
    return asyncio.run(get_page_total(cookies))

if __name__ == "__main__":
    # 测试获取总页数
    from get_cookie import get_cookie_sync
    
    # 获取 cookie
    cookies = get_cookie_sync()
    
    # 获取总页数
    page_total, total_users = get_page_total_sync(cookies)
    
    if page_total > 0:
        print(f"用户总数: {total_users}")
        print(f"总页数: {page_total}")
    else:
        print("获取总页数失败") 