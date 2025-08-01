#!/usr/bin/env python3
"""
诊断主服务的项目提取功能
"""

import sys
sys.path.append('backend')

from backend.app.services.resume_parser import ResumeParser
import json

def test_project_extraction():
    """测试项目提取功能"""
    print("🔍 诊断主服务的项目提取功能...")
    
    # 创建解析器实例
    parser = ResumeParser()
    
    # 测试文件
    test_file = "docs/testfile/app_cv.pdf"
    
    try:
        # 解析简历
        result = parser.parse_resume(test_file, "pdf")
        
        print(f"✅ 解析成功: {result['success']}")
        
        if result['success']:
            parsed_data = result['parsed_data']
            print(f"📊 解析数据键: {list(parsed_data.keys())}")
            
            if 'projects' in parsed_data:
                projects = parsed_data['projects']
                print(f"🎯 找到项目数量: {len(projects)}")
                
                if projects:
                    print("📝 第一个项目:")
                    print(f"   - 名称: {projects[0].get('name')}")
                    print(f"   - 描述: {projects[0].get('description', '')[:100]}...")
                    print(f"   - 技术: {projects[0].get('technologies')}")
            else:
                print("❌ parsed_data中没有projects字段")
                
            # 测试直接调用_extract_projects方法
            print("\n🔧 直接测试_extract_projects方法:")
            try:
                raw_text = result['raw_text']
                direct_projects = parser._extract_projects(raw_text)
                print(f"🎯 直接提取项目数量: {len(direct_projects)}")
                
                if direct_projects:
                    print("📝 第一个直接提取的项目:")
                    print(f"   - 名称: {direct_projects[0].get('name')}")
                    print(f"   - 描述: {direct_projects[0].get('description', '')[:100]}...")
                    
            except Exception as e:
                print(f"❌ 直接提取失败: {e}")
        else:
            print(f"❌ 解析失败: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 整体测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_project_extraction() 