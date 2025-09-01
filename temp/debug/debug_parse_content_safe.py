#!/usr/bin/env python3
"""
详细调试_parse_content_safe方法
"""

import sys
sys.path.append('backend')

from backend.app.services.resume_parser import ResumeParser
import json

def debug_parse_content_safe():
    """详细调试_parse_content_safe方法"""
    print("🔍 详细调试_parse_content_safe方法...")
    
    # 创建解析器实例
    parser = ResumeParser()
    
    # 测试文件
    test_file = "docs/testfile/app_cv.pdf"
    
    try:
        # 首先获取原始文本
        with open(test_file, 'rb') as f:
            raw_text = parser._extract_pdf_text(test_file)
        
        print(f"📄 原始文本长度: {len(raw_text)}")
        print(f"📄 原始文本前100字符: {raw_text[:100]}...")
        
        # 调用_parse_content_safe方法
        print("\n🔧 调用_parse_content_safe方法...")
        result = parser._parse_content_safe(raw_text)
        
        print(f"📊 返回结果的键: {list(result.keys())}")
        
        for key, value in result.items():
            if isinstance(value, list):
                print(f"   - {key}: {len(value)} 个项目")
                if value and key == 'projects':
                    print(f"     第一个项目: {value[0]}")
            else:
                print(f"   - {key}: {value}")
        
        # 手动测试项目提取
        print("\n🔧 手动测试_extract_projects方法...")
        manual_projects = parser._extract_projects(raw_text)
        print(f"🎯 手动提取的项目数量: {len(manual_projects)}")
        
        # 比较结果
        result_projects = result.get('projects', [])
        print(f"\n📊 比较:")
        print(f"   - _parse_content_safe中的projects: {len(result_projects)}")
        print(f"   - 手动调用_extract_projects: {len(manual_projects)}")
        
        if len(result_projects) != len(manual_projects):
            print("❌ 结果不一致！")
        else:
            print("✅ 结果一致")
            
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_parse_content_safe() 