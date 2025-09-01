#!/usr/bin/env python3
"""
修复简历API以支持项目经验字段
"""

import re

def fix_resume_api():
    """修复简历API代码以包含项目字段"""
    
    # 读取原文件
    with open('backend/app/api/resumes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经包含projects字段
    if 'resume.projects = parsed_data.get' in content:
        print("✅ API代码已经包含projects字段支持")
        return
    
    # 找到需要修改的位置
    pattern = r'(resume\.education = parsed_data\.get\(\'education\', \[\]\))'
    replacement = r'''\1
                # 添加项目经验支持
                resume.projects = parsed_data.get('projects', [])'''
    
    # 替换内容
    new_content = re.sub(pattern, replacement, content)
    
    # 检查是否成功替换
    if new_content != content:
        # 写回文件
        with open('backend/app/api/resumes.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ 已更新API代码以支持projects字段")
    else:
        print("❌ 未找到需要修改的位置")
        # 手动添加
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'resume.education = parsed_data.get' in line:
                lines.insert(i + 1, '                # 添加项目经验支持')
                lines.insert(i + 2, "                resume.projects = parsed_data.get('projects', [])")
                break
        
        new_content = '\n'.join(lines)
        with open('backend/app/api/resumes.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ 手动添加了projects字段支持")

if __name__ == "__main__":
    fix_resume_api() 