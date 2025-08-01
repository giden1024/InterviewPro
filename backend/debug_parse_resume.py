#!/usr/bin/env python3
"""
Debug parse_resume method structure
"""
import os
import json
from app.services.resume_parser import ResumeParser

def debug_parse_resume():
    """调试parse_resume方法的返回结构"""
    
    # 查找最新的.doc文件
    uploads_dir = "uploads"
    doc_files = []
    
    if os.path.exists(uploads_dir):
        for root, dirs, files in os.walk(uploads_dir):
            for file in files:
                if file.endswith('.doc'):
                    file_path = os.path.join(root, file)
                    doc_files.append(file_path)
    
    if not doc_files:
        print("❌ No .doc files found")
        return
    
    doc_file = doc_files[-1]
    parser = ResumeParser()
    
    print(f"🧪 Testing file: {doc_file}")
    
    # 测试完整的parse_resume方法
    print("\n=== Testing parse_resume method ===")
    result = parser.parse_resume(doc_file, 'doc')
    
    # 打印完整的返回结构
    print("Complete result structure:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    
    # 检查具体的数据路径
    print(f"\n=== Data Path Analysis ===")
    print(f"result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    if 'data' in result:
        data = result['data']
        print(f"data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
        if isinstance(data, dict):
            print(f"name: {data.get('name', 'Not found')}")
            print(f"email: {data.get('email', 'Not found')}")
            print(f"phone: {data.get('phone', 'Not found')}")
            print(f"experience count: {len(data.get('experience', []))}")
            print(f"skills count: {len(data.get('skills', []))}")
            print(f"education count: {len(data.get('education', []))}")
    
    # 直接测试_parse_content方法
    print(f"\n=== Testing _parse_content directly ===")
    raw_text = parser._extract_text(doc_file, 'doc')
    direct_result = parser._parse_content(raw_text)
    
    print("Direct _parse_content result:")
    print(json.dumps(direct_result, indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    debug_parse_resume() 