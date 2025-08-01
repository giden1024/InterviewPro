#!/usr/bin/env python3
"""
调试工作经历和教育经历提取
"""

import os
import sys
import json
from pathlib import Path

# 添加后端路径
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'

try:
    from app.services.resume_parser import ResumeParser
    print("✅ 成功导入 ResumeParser")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def debug_experience_education_extraction():
    """调试工作经历和教育经历提取"""
    
    # 测试文件路径
    test_file = 'docs/testfile/刘婧哲 Ven.docx'
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    print(f"📁 测试文件: {test_file}")
    
    # 创建解析器实例
    parser = ResumeParser()
    
    # 1. 首先提取原始文本
    print("\n" + "="*60)
    print("1. 提取原始文本")
    print("="*60)
    
    try:
        raw_text = parser._extract_docx_text(test_file)
        print(f"✅ 原始文本长度: {len(raw_text)} 字符")
        
        # 显示文本的前1000字符
        print(f"\n📝 原始文本片段（前1000字符）:")
        print("-" * 40)
        print(raw_text[:1000])
        print("-" * 40)
        
        # 保存原始文本到文件以便详细查看
        with open('debug_raw_text.txt', 'w', encoding='utf-8') as f:
            f.write(raw_text)
        print("💾 原始文本已保存到 debug_raw_text.txt")
        
    except Exception as e:
        print(f"❌ 文本提取失败: {e}")
        return
    
    # 2. 测试工作经历提取
    print("\n" + "="*60)
    print("2. 测试工作经历提取")
    print("="*60)
    
    try:
        experiences = parser._extract_experience(raw_text)
        print(f"✅ 找到工作经历条目: {len(experiences)}")
        
        for i, exp in enumerate(experiences, 1):
            print(f"\n工作经历 {i}:")
            print(f"  公司: {exp.get('company', '未识别')}")
            print(f"  职位: {exp.get('position', '未识别')}")
            print(f"  时间: {exp.get('duration', '未识别')}")
            print(f"  描述长度: {len(exp.get('description', '') or '')} 字符")
            print(f"  原始文本片段: {exp.get('raw_text', '')[:100]}...")
        
        if not experiences:
            print("❌ 未找到任何工作经历")
            
            # 尝试手动查找工作经历关键词
            import re
            work_keywords = ['experience', 'work', '工作', 'employment', 'career', 'Ant Group', 'SparkX', 'ByteDance']
            
            print("\n🔍 手动搜索工作经历关键词:")
            for keyword in work_keywords:
                matches = list(re.finditer(re.escape(keyword), raw_text, re.IGNORECASE))
                if matches:
                    print(f"  '{keyword}': 找到 {len(matches)} 次")
                    for match in matches[:3]:  # 只显示前3个匹配
                        start = max(0, match.start() - 50)
                        end = min(len(raw_text), match.end() + 50)
                        context = raw_text[start:end].replace('\n', ' ')
                        print(f"    位置 {match.start()}: ...{context}...")
    
    except Exception as e:
        print(f"❌ 工作经历提取失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 测试教育经历提取
    print("\n" + "="*60)
    print("3. 测试教育经历提取")
    print("="*60)
    
    try:
        education = parser._extract_education(raw_text)
        print(f"✅ 找到教育经历条目: {len(education)}")
        
        for i, edu in enumerate(education, 1):
            print(f"\n教育经历 {i}:")
            print(f"  学校: {edu.get('school', '未识别')}")
            print(f"  学位: {edu.get('degree', '未识别')}")
            print(f"  时间: {edu.get('duration', '未识别')}")
            print(f"  原始文本: {edu.get('raw_text', '')[:200]}...")
        
        if not education:
            print("❌ 未找到任何教育经历")
            
            # 尝试手动查找教育经历关键词
            import re
            edu_keywords = ['education', 'academic', '教育', 'university', 'college', 'degree', 'Johns Hopkins', 'Jiaotong']
            
            print("\n🔍 手动搜索教育经历关键词:")
            for keyword in edu_keywords:
                matches = list(re.finditer(re.escape(keyword), raw_text, re.IGNORECASE))
                if matches:
                    print(f"  '{keyword}': 找到 {len(matches)} 次")
                    for match in matches[:3]:  # 只显示前3个匹配
                        start = max(0, match.start() - 50)
                        end = min(len(raw_text), match.end() + 50)
                        context = raw_text[start:end].replace('\n', ' ')
                        print(f"    位置 {match.start()}: ...{context}...")
    
    except Exception as e:
        print(f"❌ 教育经历提取失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 完整解析测试
    print("\n" + "="*60)
    print("4. 完整解析测试")
    print("="*60)
    
    try:
        result = parser._parse_content_safe(test_file)
        
        if result.get('success'):
            data = result['data']
            print(f"✅ 完整解析成功")
            print(f"  姓名: {data.get('name', '未识别')}")
            print(f"  邮箱: {data.get('email', '未识别')}")
            print(f"  电话: {data.get('phone', '未识别')}")
            print(f"  技能数量: {len(data.get('skills', []))}")
            print(f"  工作经历数量: {len(data.get('experience', []))}")
            print(f"  教育经历数量: {len(data.get('education', []))}")
            print(f"  项目经验数量: {len(data.get('projects', []))}")
            
            # 详细输出工作经历和教育经历
            if data.get('experience'):
                print("\n📝 解析出的工作经历:")
                for i, exp in enumerate(data['experience'], 1):
                    print(f"  {i}. {exp}")
            
            if data.get('education'):
                print("\n🎓 解析出的教育经历:")
                for i, edu in enumerate(data['education'], 1):
                    print(f"  {i}. {edu}")
        else:
            print(f"❌ 完整解析失败: {result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"❌ 完整解析异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_experience_education_extraction() 