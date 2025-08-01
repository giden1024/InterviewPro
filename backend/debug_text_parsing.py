#!/usr/bin/env python3
"""
Debug text parsing for .doc files
"""
import os
import re
from app.services.resume_parser import ResumeParser

def debug_text_parsing():
    """诊断文本解析问题"""
    
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
    
    # 提取原始文本
    raw_text = parser._extract_text(doc_file, 'doc')
    print(f"📝 Raw text length: {len(raw_text)}")
    print(f"🔍 First 500 characters:")
    print("=" * 50)
    print(raw_text[:500])
    print("=" * 50)
    
    # 测试姓名提取
    print("\n=== Testing Name Extraction ===")
    name = parser._extract_name(raw_text)
    print(f"Name result: {name}")
    
    # 手动测试姓名模式
    lines = raw_text.split('\n')
    print(f"First few lines:")
    for i, line in enumerate(lines[:10]):
        print(f"  {i+1}: '{line.strip()}'")
    
    # 测试邮箱提取
    print("\n=== Testing Email Extraction ===")
    email = parser._extract_email(raw_text)
    print(f"Email result: {email}")
    
    # 手动查找邮箱模式
    email_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'\b([A-Za-z0-9._%+-]+)\s+(outlook|gmail|hotmail|yahoo|qq|163|126)\s*\.?\s*(com|cn|org|net)\b'
    ]
    for i, pattern in enumerate(email_patterns):
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        print(f"  Pattern {i+1} matches: {matches}")
    
    # 测试电话提取
    print("\n=== Testing Phone Extraction ===")
    phone = parser._extract_phone(raw_text)
    print(f"Phone result: {phone}")
    
    # 手动查找电话模式
    phone_patterns = [
        r'\b1[3-9]\d{9}\b',
        r'\b1[3-9]\d{1}-\d{4}-\d{4}\b',
        r'\b1[3-9]\d{1}-\d{3}-\d{4}\b'
    ]
    for i, pattern in enumerate(phone_patterns):
        matches = re.findall(pattern, raw_text)
        print(f"  Phone pattern {i+1} matches: {matches}")

if __name__ == "__main__":
    debug_text_parsing() 