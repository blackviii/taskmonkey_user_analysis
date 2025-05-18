"""
测试主程序 - 模拟整个流程但不实际请求远程API
使用已下载的页面数据进行测试
"""

import os
import logging
from pathlib import Path
from datetime import datetime

# 导入自定义模块
from get_users_array_from_page import extract_user_data, process_html_file
from insert_users_array_to_db import insert_users_array
from db_config import init_db

def setup_logging():
    """设置日志"""
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"test_main_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('taskmonkey_test')

def test_main():
    """测试主流程"""
    logger = setup_logging()
    logger.info("开始执行测试模拟流程")
    
    # 确保数据库已初始化
    init_db()
    logger.info("数据库初始化完成")
    
    # 使用已下载的示例页面
    file_path = Path(__file__).parent / 'downloaded_page' / 'body.txt'
    
    if not file_path.exists():
        logger.error(f"示例文件不存在: {file_path}")
        return
    
    logger.info(f"使用示例文件: {file_path}")
    
    # 解析用户数据
    users_data = process_html_file(file_path)
    
    if not users_data:
        logger.error("未提取到用户数据")
        return
    
    logger.info(f"提取到 {len(users_data)} 条用户数据")
    
    # 插入到数据库
    try:
        new_users, updated_users = insert_users_array(users_data)
        logger.info(f"数据插入完成，新增用户: {new_users}, 更新用户: {updated_users}")
    except Exception as e:
        logger.error(f"数据插入失败: {e}")
        return
    
    logger.info("测试流程执行完成!")

if __name__ == "__main__":
    test_main() 