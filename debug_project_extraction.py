#!/usr/bin/env python3
"""
调试项目提取功能
"""

import os
import sys
import re
from pathlib import Path

# 添加backend模块路径
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.services.resume_parser import ResumeParser

def debug_project_extraction():
    """调试项目提取功能"""
    parser = ResumeParser()
    
    # 测试文件
    test_file = 'docs/testfile/陈熙蕾.docx'
    
    if not os.path.exists(test_file):
        print(f"文件不存在: {test_file}")
        return
        
    print(f"调试文件: {test_file}")
    print("="*60)
    
    # 解析简历
    result = parser.parse_resume(test_file, 'docx')
    
    if not result['success']:
        print(f"解析失败: {result['error']}")
        return
    
    raw_text = result['raw_text']
    print(f"原始文本长度: {len(raw_text)} 字符")
    print("\n" + "="*60)
    print("原始文本片段:")
    print("="*60)
    print(raw_text[:1000] + "..." if len(raw_text) > 1000 else raw_text)
    
    print("\n" + "="*60)
    print("测试项目提取正则表达式:")
    print("="*60)
    
    # 测试项目section模式
    project_section_patterns = [
        r'(?:projects?|项目|项目经验|作品|portfolio)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|experience|education|skills|技能|工作|教育|$)',
        r'(?:personal\s*projects?|个人项目)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|experience|education|skills|技能|工作|教育|$)',
        r'(?:academic\s*projects?|学术项目)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|experience|education|skills|技能|工作|教育|$)',
        r'(?:capstone\s*projects?|毕业项目)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|experience|education|skills|技能|工作|教育|$)'
    ]
    
    for i, pattern in enumerate(project_section_patterns):
        print(f"\n测试模式 {i+1}: {pattern}")
        matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        if matches:
            print(f"  ✅ 找到匹配: {len(matches)} 个")
            for j, match in enumerate(matches):
                print(f"    匹配 {j+1}: '{match[:100]}...' " if len(match) > 100 else f"    匹配 {j+1}: '{match}'")
        else:
            print(f"  ❌ 无匹配")
    
    print("\n" + "="*60)
    print("寻找包含项目关键词的行:")
    print("="*60)
    
    project_keywords = ['project', 'capstone', 'design project', '项目', '毕业设计', '课程设计']
    lines = raw_text.split('\n')
    
    project_lines = []
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in project_keywords):
            project_lines.append((i, line.strip()))
    
    if project_lines:
        print(f"找到 {len(project_lines)} 行包含项目关键词:")
        for line_num, line in project_lines[:10]:  # 只显示前10行
            print(f"  行 {line_num}: '{line[:80]}...' " if len(line) > 80 else f"  行 {line_num}: '{line}'")
    else:
        print("未找到包含项目关键词的行")
    
    print("\n" + "="*60)
    print("直接调用_extract_projects方法:")
    print("="*60)
    
    try:
        projects = parser._extract_projects(raw_text)
        if projects:
            print(f"✅ 成功提取 {len(projects)} 个项目:")
            for i, project in enumerate(projects):
                print(f"\n项目 {i+1}:")
                print(f"  名称: {project.get('name', 'N/A')}")
                print(f"  类型: {project.get('type', 'N/A')}")
                print(f"  技术: {project.get('technologies', [])}")
                print(f"  描述: {project.get('description', 'N/A')[:100]}...")
        else:
            print("❌ 未提取到项目")
    except Exception as e:
        print(f"❌ 提取异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_project_extraction() 