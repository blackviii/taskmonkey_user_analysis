import json
import sqlite3
from datetime import datetime
from db_config import get_db_connection, init_db

def insert_or_update_user(conn, user_data):
    """
    将用户数据插入数据库，如果已存在则更新
    
    参数:
        conn: 数据库连接
        user_data: 用户数据字典
    
    返回:
        bool: 是否为新插入的用户
    """
    cursor = conn.cursor()
    
    # 检查用户是否已存在
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_data['user_id'],))
    existing_user = cursor.fetchone()
    
    # 准备用户基本数据
    user_values = (
        user_data['user_id'],
        user_data['email'],
        user_data['create_time'],
        user_data['promotion_count'],
        user_data['is_member'],
        user_data['refund_amount'],
        user_data['last_refund_amount'],
        user_data['last_deductible_amount'],
        user_data['credit_balance'],
        user_data['has_card'],
        user_data['country'],
        user_data['recharge_amount'],
        user_data['total_deduction'],
        user_data['version'],
        user_data['terminal_type'],
        user_data['browser_type'],
        user_data['remark'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    is_new_user = False
    
    if existing_user:
        # 更新已存在的用户
        cursor.execute("""
        UPDATE users SET 
            email = ?, create_time = ?, promotion_count = ?, is_member = ?,
            refund_amount = ?, last_refund_amount = ?, last_deductible_amount = ?,
            credit_balance = ?, has_card = ?, country = ?, recharge_amount = ?,
            total_deduction = ?, version = ?, terminal_type = ?, browser_type = ?,
            remark = ?, updated_at = ?
        WHERE user_id = ?
        """, user_values[1:] + (user_data['user_id'],))
    else:
        # 插入新用户
        cursor.execute("""
        INSERT INTO users (
            user_id, email, create_time, promotion_count, is_member, 
            refund_amount, last_refund_amount, last_deductible_amount, 
            credit_balance, has_card, country, recharge_amount, 
            total_deduction, version, terminal_type, browser_type, 
            remark, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, user_values)
        is_new_user = True
    
    # 如果有链接数据，先删除旧的再插入新的
    if 'links' in user_data and user_data['links']:
        cursor.execute("DELETE FROM user_links WHERE user_id = ?", (user_data['user_id'],))
        
        for link in user_data['links']:
            cursor.execute("""
            INSERT INTO user_links (user_id, link_type, link_url)
            VALUES (?, ?, ?)
            """, (user_data['user_id'], link['link_type'], link['link_url']))
    
    return is_new_user

def insert_users_array(users_data):
    """
    将用户数据数组插入到数据库
    
    参数:
        users_data: 用户数据字典列表
    
    返回:
        tuple: (新插入用户数, 更新用户数)
    """
    # 确保数据库表已创建
    init_db()
    
    conn = get_db_connection()
    new_users = 0
    updated_users = 0
    
    try:
        # 开始事务
        conn.execute("BEGIN TRANSACTION")
        
        for user_data in users_data:
            is_new = insert_or_update_user(conn, user_data)
            if is_new:
                new_users += 1
            else:
                updated_users += 1
        
        # 提交事务
        conn.commit()
    except Exception as e:
        # 发生错误时回滚
        conn.rollback()
        print(f"数据库操作错误: {e}")
        raise
    finally:
        conn.close()
    
    return (new_users, updated_users)

if __name__ == "__main__":
    # 测试从文件读取数据并插入数据库
    import os
    from get_users_array_from_page import process_html_file
    
    file_path = os.path.join(os.path.dirname(__file__), 'downloaded_page', 'body.txt')
    users_data = process_html_file(file_path)
    
    if users_data:
        new_users, updated_users = insert_users_array(users_data)
        print(f"处理完成! 新增用户: {new_users}, 更新用户: {updated_users}") 