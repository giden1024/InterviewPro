#!/usr/bin/env python3
"""
修复简历API以包含projects字段的脚本
"""

import re

def fix_resume_api():
    """修复简历API代码以包含projects字段"""
    
    api_file = 'backend/app/api/resumes.py'
    
    # 读取原文件
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换保存逻辑
    pattern = r'(resume\.education = parsed_data\.get\(\'education\', \[\]\))'
    replacement = r'''\1
                resume.projects = parsed_data.get('projects', [])'''
    
    # 应用替换
    new_content = re.sub(pattern, replacement, content)
    
    # 如果没有找到替换点，手动插入
    if new_content == content:
        # 寻找教育背景保存的位置
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'resume.education = parsed_data.get(\'education\', [])' in line:
                # 在下一行插入projects字段
                lines.insert(i + 1, '                resume.projects = parsed_data.get(\'projects\', [])')
                break
        new_content = '\n'.join(lines)
    
    # 保存修改后的文件
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 已修复简历API，添加projects字段支持")

if __name__ == "__main__":
    fix_resume_api() 