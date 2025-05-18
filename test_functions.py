import os
import pytest
import json
import sqlite3
from pathlib import Path

# 导入被测试的模块
from get_users_array_from_page import extract_user_data, extract_total_users, process_html_file
from insert_users_array_to_db import insert_users_array
from db_config import get_db_connection, init_db

# 测试数据路径
TEST_DATA_PATH = Path(__file__).parent / 'downloaded_page' / 'body.txt'

@pytest.fixture
def sample_html_content():
    """读取示例HTML内容作为测试数据"""
    if TEST_DATA_PATH.exists():
        with open(TEST_DATA_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return ""

@pytest.fixture
def init_test_db():
    """初始化测试数据库"""
    # 使用内存数据库进行测试
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # 创建测试表
    cursor = conn.cursor()
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
    
    yield conn
    
    # 关闭连接
    conn.close()

def test_extract_total_users(sample_html_content):
    """测试提取用户总数"""
    if not sample_html_content:
        pytest.skip("没有测试数据，跳过测试")
    
    total_users = extract_total_users(sample_html_content)
    assert isinstance(total_users, int)
    assert total_users > 0
    print(f"提取到的用户总数: {total_users}")

def test_extract_user_data(sample_html_content):
    """测试从HTML提取用户数据"""
    if not sample_html_content:
        pytest.skip("没有测试数据，跳过测试")
    
    users_data = extract_user_data(sample_html_content)
    assert isinstance(users_data, list)
    assert len(users_data) > 0
    
    # 检查第一个用户的数据结构
    first_user = users_data[0]
    assert 'user_id' in first_user
    assert 'email' in first_user
    assert 'create_time' in first_user
    assert 'links' in first_user
    
    print(f"提取到 {len(users_data)} 条用户数据")
    print(f"第一条用户数据: {first_user['user_id']} - {first_user['email']}")

def test_process_html_file():
    """测试处理HTML文件"""
    if not TEST_DATA_PATH.exists():
        pytest.skip("测试文件不存在，跳过测试")
    
    users_data = process_html_file(TEST_DATA_PATH)
    assert isinstance(users_data, list)
    assert len(users_data) > 0
    
    print(f"从文件提取到 {len(users_data)} 条用户数据")

def test_insert_users_array(init_test_db, sample_html_content):
    """测试插入用户数据到数据库"""
    if not sample_html_content:
        pytest.skip("没有测试数据，跳过测试")
    
    # 提取测试数据
    users_data = extract_user_data(sample_html_content)
    assert len(users_data) > 0
    
    # 插入数据库
    conn = init_test_db
    
    # 替换 get_db_connection 函数，返回测试连接
    def mock_get_db_connection():
        return conn
    
    # 插入数据
    from insert_users_array_to_db import insert_or_update_user
    
    for user_data in users_data[:3]:  # 只测试前三条
        is_new = insert_or_update_user(conn, user_data)
        assert is_new == True  # 第一次插入应该是新记录
    
    conn.commit()
    
    # 验证插入结果
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    assert count > 0
    
    # 测试更新
    if len(users_data) > 0:
        # 修改第一个用户的数据
        users_data[0]['remark'] = "测试更新"
        is_new = insert_or_update_user(conn, users_data[0])
        assert is_new == False  # 此时应该是更新操作
        
        # 验证更新结果
        cursor = conn.cursor()
        cursor.execute("SELECT remark FROM users WHERE user_id = ?", (users_data[0]['user_id'],))
        updated_remark = cursor.fetchone()[0]
        assert updated_remark == "测试更新"
    
    print("数据库插入和更新测试通过")

if __name__ == "__main__":
    # 运行测试
    pytest.main(["-v", __file__]) 