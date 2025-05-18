import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
from db_config import get_db_connection

def export_users_to_excel():
    """
    将users.db中的用户数据导出到Excel文件
    """
    conn = get_db_connection()
    
    try:
        # 获取用户数据
        users_df = pd.read_sql_query("SELECT * FROM users ORDER BY user_id DESC", conn)
        
        # 获取链接数据
        links_df = pd.read_sql_query("SELECT * FROM user_links", conn)
        
        # 为每个用户创建链接信息汇总列
        links_summary = {}
        
        for user_id in users_df['user_id']:
            # 获取该用户的所有链接
            user_links = links_df[links_df['user_id'] == user_id]
            
            if not user_links.empty:
                links_text = []
                for _, link in user_links.iterrows():
                    links_text.append(f"{link['link_type']}: {link['link_url']}")
                
                links_summary[user_id] = "\n".join(links_text)
            else:
                links_summary[user_id] = ""
        
        # 将链接信息添加到用户数据中
        users_df['links_info'] = users_df['user_id'].map(links_summary)
        
        # 创建输出目录
        output_dir = Path(__file__).parent / 'exports'
        output_dir.mkdir(exist_ok=True)
        
        # 设置输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"taskmonkey_users_info_{timestamp}.xlsx"
        
        # 导出到Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 用户数据表
            users_df.to_excel(writer, sheet_name='用户数据', index=False)
            
            # 链接数据表
            links_df.to_excel(writer, sheet_name='链接数据', index=False)
            
            # 国家统计表
            country_stats = users_df.groupby('country').size().reset_index(name='用户数量')
            country_stats.to_excel(writer, sheet_name='国家分布', index=False)
            
            # 会员统计表
            member_stats = users_df.groupby('is_member').size().reset_index(name='用户数量')
            member_stats.to_excel(writer, sheet_name='会员统计', index=False)
        
        print(f"数据已成功导出到: {output_file}")
        return output_file
    
    finally:
        conn.close()

if __name__ == "__main__":
    # 检查是否缺少openpyxl库
    try:
        import openpyxl
    except ImportError:
        print("缺少openpyxl库，正在安装...")
        import subprocess
        subprocess.check_call(["pip", "install", "openpyxl"])
        print("openpyxl库安装完成")
    
    # 导出数据
    output_file = export_users_to_excel()
    
    # 打印输出文件大小
    file_size_kb = Path(output_file).stat().st_size / 1024
    print(f"文件大小: {file_size_kb:.2f} KB") 