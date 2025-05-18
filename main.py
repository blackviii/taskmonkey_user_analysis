import os
import time
import logging
from datetime import datetime
from pathlib import Path

# 导入自定义模块
from get_cookie import get_cookie_sync
from get_page_total import get_page_total_sync
from get_page_content import get_page_content_sync
from get_users_array_from_page import extract_user_data
from insert_users_array_to_db import insert_users_array
from db_config import init_db

# 设置日志
def setup_logging():
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"taskmonkey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('taskmonkey')

def main():
    """主程序入口"""
    logger = setup_logging()
    logger.info("开始执行用户数据采集")
    
    # 确保数据库已初始化
    init_db()
    logger.info("数据库初始化完成")
    
    # 第一步：获取cookie
    logger.info("正在获取cookie...")
    cookies = get_cookie_sync()
    if not cookies:
        logger.error("获取cookie失败，程序退出")
        return
    logger.info(f"成功获取cookie: {list(cookies.keys())}")
    
    # 第二步：获取总页数
    logger.info("正在获取总页数...")
    page_total, total_users = get_page_total_sync(cookies)
    if page_total <= 0:
        logger.error("获取总页数失败，程序退出")
        return
    logger.info(f"用户总数: {total_users}, 总页数: {page_total}")
    
    # 第三步：逐页获取用户数据并插入数据库
    total_new_users = 0
    total_updated_users = 0
    
    for page_num in range(1, page_total + 1):
        try:
            logger.info(f"正在处理第 {page_num}/{page_total} 页...")
            
            # 构建页面URL
            page_url = f"https://api.taskmonkey.ai/api/user/index?orderBy=id&page={page_num}"
            
            # 获取页面内容
            save_path = Path(__file__).parent / 'downloaded_page' / f'page_{page_num}.html'
            content = get_page_content_sync(page_url, cookies, save_path)
            
            if not content:
                logger.error(f"获取第 {page_num} 页内容失败，跳过此页")
                continue
            
            # 解析用户数据
            users_data = extract_user_data(content)
            
            if not users_data:
                logger.warning(f"第 {page_num} 页未提取到用户数据，跳过此页")
                continue
            
            logger.info(f"第 {page_num} 页提取到 {len(users_data)} 条用户数据")
            
            # 插入到数据库
            new_users, updated_users = insert_users_array(users_data)
            total_new_users += new_users
            total_updated_users += updated_users
            
            logger.info(f"第 {page_num} 页处理完成，新增用户: {new_users}, 更新用户: {updated_users}")
            
            # 添加延时防止请求过快
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"处理第 {page_num} 页时出错: {e}")
            continue
    
    logger.info("用户数据采集完成!")
    logger.info(f"总共处理用户数: {total_new_users + total_updated_users}")
    logger.info(f"新增用户: {total_new_users}, 更新用户: {total_updated_users}")

if __name__ == "__main__":
    main() 