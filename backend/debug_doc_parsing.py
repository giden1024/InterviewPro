#!/usr/bin/env python3
"""
Debug .doc file parsing issue
"""
import os
import sys
import traceback
from docx import Document

def test_doc_parsing():
    """测试.doc文件解析"""
    
    # 查找最近的.doc文件
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        for root, dirs, files in os.walk(uploads_dir):
            for file in files:
                if file.endswith('.doc'):
                    file_path = os.path.join(root, file)
                    print(f"Found .doc file: {file_path}")
                    print(f"File size: {os.path.getsize(file_path)} bytes")
                    print(f"File exists: {os.path.exists(file_path)}")
                    
                    # 测试用python-docx直接解析
                    try:
                        print("\n=== Testing python-docx ===")
                        doc = Document(file_path)
                        print("SUCCESS: python-docx worked!")
                        text = ""
                        for paragraph in doc.paragraphs:
                            text += paragraph.text + "\n"
                        print(f"Extracted text length: {len(text)}")
                        return
                    except Exception as e:
                        print(f"python-docx failed: {e}")
                        print(f"Error type: {type(e).__name__}")
                        print(f"Error string contains 'Package not found': {'Package not found' in str(e)}")
                        print(f"Error string contains 'PackageNotFoundError': {'PackageNotFoundError' in str(e)}")
                        print(f"Error string contains 'File is not a zip file': {'File is not a zip file' in str(e)}")
                        
                        # 测试olefile
                        try:
                            print("\n=== Testing olefile ===")
                            import olefile
                            if olefile.isOleFile(file_path):
                                print("SUCCESS: File is recognized as OLE format")
                                
                                # 测试我们的解析器
                                print("\n=== Testing our resume parser ===")
                                from app.services.resume_parser import ResumeParser
                                parser = ResumeParser()
                                result = parser._extract_doc_text_fallback(file_path)
                                print(f"Our parser result length: {len(result)}")
                                print(f"First 200 chars: {result[:200]}")
                                
                            else:
                                print("File is not in OLE format")
                        except Exception as ole_e:
                            print(f"olefile failed: {ole_e}")
                            traceback.print_exc()
                    
                    break
    else:
        print("No uploads directory found")

if __name__ == "__main__":
    test_doc_parsing() 