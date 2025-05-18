import sqlite3
import json
from pathlib import Path
from db_config import get_db_connection

def query_users(limit=10):
    """
    查询用户数据
    
    参数:
        limit: 限制返回结果数量
        
    返回:
        用户数据列表
    """
    conn = get_db_connection()
    
    try:
        # 查询用户基本信息
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM users 
        ORDER BY user_id DESC
        LIMIT ?
        """, (limit,))
        
        users = []
        for user_row in cursor.fetchall():
            user_data = dict(user_row)
            
            # 查询关联的链接
            link_cursor = conn.cursor()
            link_cursor.execute("""
            SELECT link_type, link_url FROM user_links
            WHERE user_id = ?
            """, (user_data['user_id'],))
            
            links = [dict(link) for link in link_cursor.fetchall()]
            user_data['links'] = links
            
            users.append(user_data)
            
        return users
    finally:
        conn.close()

def count_users():
    """
    统计用户数量
    
    返回:
        总用户数、会员数、非会员数
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        
        # 总用户数
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        
        # 会员数
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_member = '是'")
        members = cursor.fetchone()[0]
        
        # 非会员数
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_member = '否'")
        non_members = cursor.fetchone()[0]
        
        return total, members, non_members
    finally:
        conn.close()

def get_country_stats():
    """
    获取国家分布统计
    
    返回:
        国家分布字典
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT country, COUNT(*) as count
        FROM users
        GROUP BY country
        ORDER BY count DESC
        """)
        
        country_stats = {}
        for row in cursor.fetchall():
            country_stats[row['country']] = row['count']
            
        return country_stats
    finally:
        conn.close()

if __name__ == "__main__":
    # 统计用户数量
    total, members, non_members = count_users()
    print(f"总用户数: {total}")
    print(f"会员数: {members}")
    print(f"非会员数: {non_members}")
    print()
    
    # 获取国家分布
    country_stats = get_country_stats()
    print("国家分布:")
    for country, count in country_stats.items():
        print(f"  {country}: {count}")
    print()
    
    # 查询最新用户
    users = query_users(5)
    print(f"最新 {len(users)} 条用户数据:")
    for user in users:
        print(f"  ID: {user['user_id']}, 邮箱: {user['email']}, 创建时间: {user['create_time']}")
        print(f"  会员状态: {user['is_member']}, 国家: {user['country']}, 积分余额: {user['credit_balance']}")
        print(f"  链接数量: {len(user['links'])}")
        print() 