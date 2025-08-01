#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.resume_parser import ResumeParser

def debug_resume_parsing(file_path):
    """调试简历解析过程"""
    print(f"🔍 开始调试简历文件: {file_path}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 获取文件类型
    file_type = Path(file_path).suffix.lower().lstrip('.')
    print(f"📄 文件类型: {file_type}")
    
    # 创建解析器
    parser = ResumeParser()
    
    try:
        # 1. 提取原始文本
        print("\n📝 步骤1: 提取原始文本")
        raw_text = parser._extract_text(file_path, file_type)
        print(f"✅ 提取成功，文本长度: {len(raw_text)} 字符")
        
        # 显示前500字符
        print("\n📖 原始文本预览 (前500字符):")
        print("-" * 40)
        print(repr(raw_text[:500]))
        print("-" * 40)
        
        # 2. 检查工作经历部分
        print("\n🔍 步骤2: 分析工作经历部分")
        
        # 查找所有可能的工作经历标题
        experience_patterns = [
            r'work\s*experience',
            r'professional\s*experience', 
            r'employment\s*history',
            r'career\s*history',
            r'experience',
            r'employment',
            r'工作经历',
            r'工作经验',
            r'职业经历'
        ]
        
        found_sections = []
        for pattern in experience_patterns:
            matches = re.finditer(pattern, raw_text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(raw_text), match.end() + 200)
                context = raw_text[start:end]
                found_sections.append({
                    'pattern': pattern,
                    'position': match.start(),
                    'context': context
                })
        
        if found_sections:
            print(f"✅ 找到 {len(found_sections)} 个可能的工作经历标题:")
            for i, section in enumerate(found_sections):
                print(f"\n标题 {i+1}: 模式 '{section['pattern']}' (位置: {section['position']})")
                print("上下文:")
                print(repr(section['context']))
        else:
            print("❌ 未找到工作经历标题")
        
        # 3. 使用现有逻辑提取工作经历
        print("\n🔧 步骤3: 使用现有逻辑提取")
        experiences = parser._extract_experience(raw_text)
        print(f"📊 提取结果: {len(experiences)} 个工作经历")
        
        for i, exp in enumerate(experiences):
            print(f"\n工作经历 {i+1}:")
            print(f"  公司: {exp.get('company', '未知')}")
            print(f"  职位: {exp.get('position', '未知')}")
            print(f"  时间: {exp.get('duration', '未知')}")
            print(f"  原始文本: {exp.get('raw_text', '')[:100]}...")
        
        # 4. 尝试改进的提取逻辑
        print("\n🚀 步骤4: 尝试改进的提取逻辑")
        improved_experiences = extract_experience_improved(raw_text)
        print(f"📊 改进提取结果: {len(improved_experiences)} 个工作经历")
        
        for i, exp in enumerate(improved_experiences):
            print(f"\n改进结果 {i+1}:")
            print(f"  公司: {exp.get('company', '未知')}")
            print(f"  职位: {exp.get('position', '未知')}")
            print(f"  时间: {exp.get('duration', '未知')}")
            print(f"  原始文本: {exp.get('raw_text', '')[:100]}...")
        
        # 5. 完整解析测试
        print("\n📋 步骤5: 完整解析测试")
        result = parser.parse_resume(file_path, file_type)
        
        if result['success']:
            parsed_data = result['parsed_data']
            print("✅ 解析成功!")
            print(f"  姓名: {parsed_data.get('name', '未识别')}")
            print(f"  邮箱: {parsed_data.get('email', '未识别')}")
            print(f"  电话: {parsed_data.get('phone', '未识别')}")
            print(f"  技能数量: {len(parsed_data.get('skills', []))}")
            print(f"  工作经历数量: {len(parsed_data.get('experience', []))}")
            print(f"  教育背景数量: {len(parsed_data.get('education', []))}")
        else:
            print(f"❌ 解析失败: {result['error']}")
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

def extract_experience_improved(text: str) -> list:
    """改进的工作经历提取逻辑"""
    experiences = []
    
    # 更灵活的工作经历标题匹配
    exp_pattern = r'(?:work\s*experience|professional\s*experience|employment\s*history|career\s*history|experience|employment|工作经历|工作经验|职业经历)[:\s]*'
    
    # 查找工作经历部分
    exp_matches = list(re.finditer(exp_pattern, text, re.IGNORECASE))
    
    for match in exp_matches:
        start_pos = match.end()
        
        # 查找下一个主要部分的开始
        next_section_pattern = r'\n\s*(?:education|skills|技能|教育|projects|项目|certifications|证书|references|推荐)'
        next_match = re.search(next_section_pattern, text[start_pos:], re.IGNORECASE)
        
        if next_match:
            end_pos = start_pos + next_match.start()
        else:
            end_pos = len(text)
        
        # 提取这一部分的文本
        section_text = text[start_pos:end_pos].strip()
        
        if section_text:
            print(f"🔍 找到工作经历部分 (长度: {len(section_text)}):")
            print("-" * 30)
            print(section_text[:300] + "..." if len(section_text) > 300 else section_text)
            print("-" * 30)
            
            # 尝试分割工作经历条目
            # 按空行分割
            jobs = re.split(r'\n\s*\n', section_text)
            
            for job in jobs:
                job = job.strip()
                if job and len(job) > 20:  # 过滤太短的文本
                    experiences.append({
                        'raw_text': job,
                        'company': extract_company_improved(job),
                        'position': extract_position_improved(job),
                        'duration': extract_duration_improved(job)
                    })
    
    return experiences

def extract_company_improved(text: str) -> str:
    """改进的公司名提取"""
    # 常见的公司名模式
    patterns = [
        r'(?:at\s+|@\s*)([A-Z][A-Za-z\s&.,]+?)(?:\s*[,\n]|\s*$)',
        r'^([A-Z][A-Za-z\s&.,]+?)(?:\s*[,\n]|\s+\d{4})',
        r'([A-Z][A-Za-z\s&.,]+?)\s*(?:Inc|Corp|Ltd|LLC|Co)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            company = match.group(1).strip()
            if len(company) > 2 and len(company) < 50:
                return company
    
    return None

def extract_position_improved(text: str) -> str:
    """改进的职位提取"""
    lines = text.split('\n')
    for line in lines[:3]:  # 检查前几行
        line = line.strip()
        if line and not re.search(r'\d{4}', line):  # 不包含年份的行
            # 移除公司名等信息
            cleaned = re.sub(r'\s*(?:at\s+|@\s*)[A-Z].*', '', line)
            if cleaned and len(cleaned) > 3 and len(cleaned) < 100:
                return cleaned.strip()
    return None

def extract_duration_improved(text: str) -> str:
    """改进的时间段提取"""
    # 匹配各种时间格式
    patterns = [
        r'(\d{4})\s*[-–—]\s*(\d{4})',
        r'(\d{4})\s*[-–—]\s*present',
        r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4})',
        r'(\w+\s+\d{4})\s*[-–—]\s*present'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

if __name__ == "__main__":
    # 使用用户提供的文件路径
    file_path = "/Users/mayuyang/InterviewPro/temp/resume.doc"
    debug_resume_parsing(file_path) 