#!/usr/bin/env python3
"""
最终版：针对特殊Unicode字符格式的提取方法
"""

import re
from typing import List, Dict, Optional

def final_extract_education(text: str) -> List[Dict]:
    """最终版教育经历提取 - 专门处理​​标记的格式"""
    education_list = []
    
    # 查找教育部分
    education_start = text.find('Education')
    work_start = text.find('Work Experience')
    
    if education_start != -1 and work_start != -1:
        education_section = text[education_start:work_start].strip()
        print(f"[DEBUG] 教育部分原始内容:\n{education_section}\n")
        
        # 查找所有被​​包围的大学名称
        university_pattern = r'​​([^​]+?(?:University|College|Institute|School)[^​]*)​​'
        universities = re.findall(university_pattern, education_section)
        
        print(f"[DEBUG] 找到大学: {universities}")
        
        for university in universities:
            university = university.strip()
            if len(university) > 5:  # 确保是有效的大学名
                print(f"[DEBUG] 处理大学: {university}")
                
                # 查找这个大学后面的详细信息
                uni_start = education_section.find(f'​​{university}​​')
                if uni_start != -1:
                    # 查找下一个大学的开始位置或部分结束位置
                    next_uni_start = len(education_section)
                    for other_uni in universities:
                        if other_uni != university:
                            other_start = education_section.find(f'​​{other_uni}​​', uni_start + 1)
                            if other_start != -1:
                                next_uni_start = min(next_uni_start, other_start)
                    
                    # 提取这个大学的详细信息
                    uni_section = education_section[uni_start:next_uni_start].strip()
                    print(f"[DEBUG] 大学详细信息:\n{uni_section}\n")
                    
                    # 提取学位信息
                    degree = None
                    degree_patterns = [
                        r'(MS in [^|]+)',
                        r'(BSc in [^|]+)', 
                        r'(MA in [^|]+)',
                        r'(BA in [^|]+)',
                        r'(PhD in [^|]+)',
                        r'(Bachelor[^|]+)',
                        r'(Master[^|]+)'
                    ]
                    
                    for pattern in degree_patterns:
                        degree_match = re.search(pattern, uni_section)
                        if degree_match:
                            degree = degree_match.group(1).strip()
                            break
                    
                    # 提取时间
                    duration_pattern = r'(\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4})'
                    duration_match = re.search(duration_pattern, uni_section)
                    duration = duration_match.group(1).strip() if duration_match else None
                    
                    # 提取地点
                    location = None
                    if 'USA' in uni_section:
                        location = 'Washington, D.C., USA'
                    elif 'China' in uni_section:
                        location = 'Suzhou, China'
                    
                    # 提取其他信息（GPA等）
                    gpa_match = re.search(r'GPA:\s*([\d.]+)', uni_section)
                    gpa = gpa_match.group(1) if gpa_match else None
                    
                    education_item = {
                        'raw_text': uni_section,
                        'school': university,
                        'degree': degree,
                        'duration': duration,
                        'location': location,
                        'gpa': gpa
                    }
                    education_list.append(education_item)
                    print(f"[DEBUG] 提取结果: {education_item}")
    
    return education_list

def final_extract_experience(text: str) -> List[Dict]:
    """最终版工作经历提取 - 专门处理​​标记的格式"""
    experience_list = []
    
    # 查找工作经历部分
    work_start = text.find('Work Experience')
    research_start = text.find('Research Experience')
    
    if work_start != -1:
        # 确定工作经历部分的结束位置
        work_end = len(text)
        if research_start != -1 and research_start > work_start:
            work_end = research_start
        
        work_section = text[work_start:work_end].strip()
        print(f"[DEBUG] 工作经历部分原始内容:\n{work_section[:500]}...\n")
        
        # 查找所有被​​包围的公司名称
        company_pattern = r'​​([^​]+?)​​\s*\|\s*([^|]+?)\s*\|\s*(\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4})'
        companies = re.findall(company_pattern, work_section)
        
        print(f"[DEBUG] 找到公司匹配: {len(companies)} 个")
        for i, (company, location, duration) in enumerate(companies):
            print(f"[DEBUG] 公司 {i+1}: {company.strip()} | {location.strip()} | {duration.strip()}")
        
        for company, location, duration in companies:
            company = company.strip()
            location = location.strip()
            duration = duration.strip()
            
            print(f"[DEBUG] 处理公司: {company}")
            
            # 查找这个公司后面的详细信息
            company_start = work_section.find(f'​​{company}​​')
            if company_start != -1:
                # 查找下一个公司的开始位置
                next_company_start = len(work_section)
                for other_company, _, _ in companies:
                    other_company = other_company.strip()
                    if other_company != company:
                        other_start = work_section.find(f'​​{other_company}​​', company_start + 1)
                        if other_start != -1:
                            next_company_start = min(next_company_start, other_start)
                
                # 提取这个公司的详细信息
                company_section = work_section[company_start:next_company_start].strip()
                print(f"[DEBUG] 公司详细信息长度: {len(company_section)} 字符")
                
                # 从公司部分第一个换行后的内容中提取职位
                lines = company_section.split('\n')
                position = None
                description_lines = []
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if i == 1 and line and not line.startswith('​​'):  # 第二行通常是职位
                        position = line
                    elif i > 1 and line:  # 其余内容作为描述
                        description_lines.append(line)
                
                description = '\n'.join(description_lines) if description_lines else None
                
                experience_item = {
                    'raw_text': company_section,
                    'company': company,
                    'position': position,
                    'duration': duration,
                    'location': location,
                    'description': description[:500] if description else None  # 限制描述长度
                }
                experience_list.append(experience_item)
                print(f"[DEBUG] 工作经历提取结果: 公司={company}, 职位={position}, 时间={duration}")
    
    return experience_list

def test_final_extraction():
    """测试最终版提取方法"""
    
    # 读取原始文本
    try:
        with open('debug_raw_text.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print("❌ 请先运行 debug_experience_education.py 生成 debug_raw_text.txt")
        return
    
    print("="*80)
    print("最终版教育经历提取测试")
    print("="*80)
    
    education = final_extract_education(text)
    print(f"\n✅ 最终找到教育经历: {len(education)} 条")
    
    for i, edu in enumerate(education, 1):
        print(f"\n📚 教育经历 {i}:")
        print(f"  🏫 学校: {edu['school']}")
        print(f"  🎓 学位: {edu['degree']}")
        print(f"  📅 时间: {edu['duration']}")
        print(f"  📍 地点: {edu['location']}")
        print(f"  📊 GPA: {edu.get('gpa', 'N/A')}")
    
    print("\n" + "="*80)
    print("最终版工作经历提取测试")
    print("="*80)
    
    experience = final_extract_experience(text)
    print(f"\n✅ 最终找到工作经历: {len(experience)} 条")
    
    for i, exp in enumerate(experience, 1):
        print(f"\n💼 工作经历 {i}:")
        print(f"  🏢 公司: {exp['company']}")
        print(f"  👔 职位: {exp['position']}")
        print(f"  📅 时间: {exp['duration']}")
        print(f"  📍 地点: {exp['location']}")
        print(f"  📝 描述长度: {len(exp['description'] or '')} 字符")
        if exp['description']:
            print(f"  📄 描述预览: {exp['description'][:100]}...")

if __name__ == "__main__":
    test_final_extraction() 