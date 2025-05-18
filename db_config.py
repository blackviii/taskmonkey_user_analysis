import os
import sqlite3
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / 'users.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        create_time TEXT NOT NULL,
        promotion_count INTEGER DEFAULT 0,
        is_member TEXT,
        refund_amount REAL DEFAULT 0,
        last_refund_amount REAL DEFAULT 0,
        last_deductible_amount REAL DEFAULT 0,
        credit_balance REAL DEFAULT 0,
        has_card TEXT,
        country TEXT,
        recharge_amount REAL DEFAULT 0,
        total_deduction REAL DEFAULT 0,
        version TEXT,
        terminal_type TEXT,
        browser_type TEXT,
        remark TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建操作链接表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        link_type TEXT NOT NULL,
        link_url TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db() 