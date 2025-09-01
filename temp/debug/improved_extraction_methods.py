#!/usr/bin/env python3
"""
改进版的工作经历和教育经历提取方法
"""

import re
from typing import List, Dict, Optional

def improved_extract_education(text: str) -> List[Dict]:
    """改进版教育经历提取"""
    education_list = []
    
    # 清理文本，移除特殊字符
    clean_text = re.sub(r'​', '', text)  # 移除特殊Unicode字符
    
    # 查找教育部分
    education_pattern = r'(?:Education|教育背景|学历)(.*?)(?:Work Experience|工作经历|Experience|Project|Skills|$)'
    education_match = re.search(education_pattern, clean_text, re.IGNORECASE | re.DOTALL)
    
    if education_match:
        education_section = education_match.group(1).strip()
        print(f"[DEBUG] 找到教育部分: {len(education_section)} 字符")
        
        # 按大学名称分割
        # 寻找大学模式：University, College, Institute, School
        university_pattern = r'([A-Z][A-Za-z\s\'-]+?(?:University|College|Institute|School)[^\n]*?(?:\n[^\n]*?)*?)(?=\n[A-Z][A-Za-z\s\'-]+?(?:University|College|Institute|School)|\n[A-Z][A-Za-z\s]+:|\nGPA|\nStudent|\nHonors|$)'
        
        universities = re.findall(university_pattern, education_section, re.MULTILINE)
        
        print(f"[DEBUG] 找到大学数量: {len(universities)}")
        
        for i, uni_text in enumerate(universities):
            uni_text = uni_text.strip()
            if len(uni_text) > 20:  # 确保有足够内容
                print(f"[DEBUG] 处理大学 {i+1}: {uni_text[:100]}...")
                
                # 提取学校名称
                school_match = re.search(r'^([A-Z][A-Za-z\s\'-]+?(?:University|College|Institute|School))', uni_text)
                school = school_match.group(1).strip() if school_match else None
                
                # 提取学位
                degree_patterns = [
                    r'((?:MS|MA|BS|BA|BSc|MSc|PhD|Bachelor|Master)[^|]*?)(?:\s*\||\s*$)',
                    r'([A-Z][A-Za-z\s]*?in\s+[A-Z][A-Za-z\s]*?)(?:\s*\||\s*$)',
                ]
                degree = None
                for pattern in degree_patterns:
                    degree_match = re.search(pattern, uni_text)
                    if degree_match:
                        degree = degree_match.group(1).strip()
                        break
                
                # 提取时间
                duration_pattern = r'(\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4})'
                duration_match = re.search(duration_pattern, uni_text)
                duration = duration_match.group(1).strip() if duration_match else None
                
                # 提取位置
                location_pattern = r'([A-Z][A-Za-z\s,\.]+(?:USA|China|UK|Canada))'
                location_match = re.search(location_pattern, uni_text)
                location = location_match.group(1).strip() if location_match else None
                
                education_item = {
                    'raw_text': uni_text,
                    'school': school,
                    'degree': degree,
                    'duration': duration,
                    'location': location
                }
                education_list.append(education_item)
                print(f"[DEBUG] 提取的教育信息: {education_item}")
    
    return education_list

def improved_extract_experience(text: str) -> List[Dict]:
    """改进版工作经历提取"""
    experience_list = []
    
    # 清理文本，移除特殊字符
    clean_text = re.sub(r'​', '', text)  # 移除特殊Unicode字符
    
    # 查找工作经历部分
    work_pattern = r'(?:Work Experience|Professional Experience|工作经历|Experience)(.*?)(?:Research Experience|Education|Skills|Project|Extracurricular|$)'
    work_match = re.search(work_pattern, clean_text, re.IGNORECASE | re.DOTALL)
    
    if work_match:
        work_section = work_match.group(1).strip()
        print(f"[DEBUG] 找到工作经历部分: {len(work_section)} 字符")
        
        # 改进的公司分割策略
        # 寻找公司模式：公司名 | 地点 | 时间
        company_pattern = r'([A-Z][A-Za-z\s\(\)\.&,-]+?)\s*\|\s*([A-Za-z\s,]+?)\s*\|\s*(\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4})(.*?)(?=\n[A-Z][A-Za-z\s\(\)\.&,-]+?\s*\|\s*[A-Za-z\s,]+?\s*\|\s*\w+\s+\d{4}|$)'
        
        companies = re.findall(company_pattern, work_section, re.DOTALL)
        
        print(f"[DEBUG] 通过公司模式找到: {len(companies)} 个工作")
        
        for i, (company, location, duration, description) in enumerate(companies):
            company = company.strip()
            location = location.strip()
            duration = duration.strip()
            description = description.strip()
            
            print(f"[DEBUG] 处理工作 {i+1}: {company}")
            
            # 从描述的第一行提取职位
            desc_lines = description.split('\n')
            position = None
            for line in desc_lines:
                line = line.strip()
                if line and not re.search(r'^(Activity|Project|Strategic|Content|Data|Brand)', line):
                    position = line
                    break
            
            # 清理描述，移除职位行
            if position:
                description = description.replace(position, '', 1).strip()
            
            experience_item = {
                'raw_text': f"{company} | {location} | {duration}\n{description}",
                'company': company,
                'position': position,
                'duration': duration,
                'location': location,
                'description': description[:500] if description else None  # 限制描述长度
            }
            experience_list.append(experience_item)
            print(f"[DEBUG] 提取的工作信息: 公司={company}, 职位={position}, 时间={duration}")
        
        # 如果上面的方法没找到足够的工作，尝试备用方法
        if len(companies) < 3:
            print("[DEBUG] 尝试备用工作提取方法...")
            
            # 备用方法：按时间模式分割
            time_based_pattern = r'(\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4})(.*?)(?=\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4}|$)'
            time_matches = re.findall(time_based_pattern, work_section, re.DOTALL)
            
            for duration, content in time_matches:
                content = content.strip()
                if len(content) > 50:  # 确保有足够内容
                    # 尝试从内容中提取公司和职位
                    lines = content.split('\n')
                    company = None
                    position = None
                    
                    for line in lines[:3]:  # 检查前3行
                        line = line.strip()
                        if '|' in line:
                            parts = [p.strip() for p in line.split('|')]
                            if len(parts) >= 2:
                                company = parts[0]
                                if len(parts) >= 3:
                                    position = parts[2] if parts[2] else None
                                break
                    
                    if company and company not in [exp['company'] for exp in experience_list]:
                        experience_item = {
                            'raw_text': content,
                            'company': company,
                            'position': position,
                            'duration': duration.strip(),
                            'location': None,
                            'description': content[:500]
                        }
                        experience_list.append(experience_item)
                        print(f"[DEBUG] 备用方法提取: 公司={company}, 时间={duration}")
    
    return experience_list

# 测试函数
def test_improved_extraction():
    """测试改进的提取方法"""
    
    # 读取原始文本
    try:
        with open('debug_raw_text.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print("❌ 请先运行 debug_experience_education.py 生成 debug_raw_text.txt")
        return
    
    print("="*60)
    print("测试改进的教育经历提取")
    print("="*60)
    
    education = improved_extract_education(text)
    print(f"✅ 找到教育经历: {len(education)} 条")
    
    for i, edu in enumerate(education, 1):
        print(f"\n教育经历 {i}:")
        print(f"  学校: {edu['school']}")
        print(f"  学位: {edu['degree']}")
        print(f"  时间: {edu['duration']}")
        print(f"  地点: {edu['location']}")
    
    print("\n" + "="*60)
    print("测试改进的工作经历提取")
    print("="*60)
    
    experience = improved_extract_experience(text)
    print(f"✅ 找到工作经历: {len(experience)} 条")
    
    for i, exp in enumerate(experience, 1):
        print(f"\n工作经历 {i}:")
        print(f"  公司: {exp['company']}")
        print(f"  职位: {exp['position']}")
        print(f"  时间: {exp['duration']}")
        print(f"  地点: {exp['location']}")
        print(f"  描述长度: {len(exp['description'] or '')} 字符")

if __name__ == "__main__":
    test_improved_extraction() 