import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

def extract_user_data(html_content):
    """
    从HTML页面内容中提取用户数据
    返回: 用户数据字典列表
    """
    soup = BeautifulSoup(html_content, 'lxml')
    users_data = []
    
    # 获取表格行数据
    table = soup.find('table')
    if not table:
        return []
    
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 18:  # 确保行有足够的列
            continue
        
        # 提取用户基本信息
        user_id = cells[0].text.strip()
        email = cells[1].text.strip()
        create_time = cells[2].text.strip()
        promotion_count = cells[3].text.strip() or '0'
        is_member = cells[4].text.strip()
        refund_amount = cells[5].text.strip() or '0'
        last_refund_amount = cells[6].text.strip() or '0'
        last_deductible_amount = cells[7].text.strip() or '0'
        credit_balance = cells[8].text.strip() or '0'
        has_card = cells[9].text.strip()
        country = cells[10].text.strip()
        recharge_amount = cells[11].text.strip() or '0'
        total_deduction = cells[12].text.strip() or '0'
        version = cells[13].text.strip()
        terminal_type = cells[14].text.strip()
        browser_type = cells[15].text.strip()
        
        # 提取操作链接
        operation_links = []
        links = cells[16].find_all('a')
        for link in links:
            if 'javascript:void(0);' not in link.get('href', ''):
                link_text = link.text.strip()
                link_url = link.get('href', '')
                operation_links.append({
                    'link_type': link_text,
                    'link_url': link_url
                })
        
        # 提取备注
        remark = cells[17].find('a').text.strip() if cells[17].find('a') else ''
        
        # 构建用户数据字典
        user_data = {
            'user_id': int(user_id),
            'email': email,
            'create_time': create_time,
            'promotion_count': int(promotion_count) if promotion_count.isdigit() else 0,
            'is_member': is_member,
            'refund_amount': float(refund_amount) if refund_amount and refund_amount != '' else 0,
            'last_refund_amount': float(last_refund_amount) if last_refund_amount and last_refund_amount != '' else 0,
            'last_deductible_amount': float(last_deductible_amount) if last_deductible_amount and last_deductible_amount != '' else 0,
            'credit_balance': float(credit_balance) if credit_balance and credit_balance != '' else 0,
            'has_card': has_card,
            'country': country,
            'recharge_amount': float(recharge_amount) if recharge_amount and recharge_amount != '' else 0,
            'total_deduction': float(total_deduction) if total_deduction and total_deduction != '' else 0,
            'version': version,
            'terminal_type': terminal_type,
            'browser_type': browser_type,
            'remark': remark,
            'links': operation_links
        }
        
        users_data.append(user_data)
    
    return users_data

def extract_total_users(html_content):
    """提取用户总数信息"""
    soup = BeautifulSoup(html_content, 'lxml')
    users_count_text = soup.find('p', string=re.compile('用户总数')).text
    users_count_match = re.search(r'用户总数: (\d+)', users_count_text)
    if users_count_match:
        return int(users_count_match.group(1))
    return 0

def process_html_file(file_path):
    """处理HTML文件并返回提取的用户数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return extract_user_data(html_content)

if __name__ == "__main__":
    # 测试从文件读取
    import os
    file_path = os.path.join(os.path.dirname(__file__), 'downloaded_page', 'body.txt')
    users_data = process_html_file(file_path)
    
    # 输出结果
    print(json.dumps(users_data, ensure_ascii=False, indent=2))
    print(f"提取到 {len(users_data)} 条用户数据") 