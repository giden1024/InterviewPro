import os
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# 文档解析库
try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None

try:
    from docx import Document
except ImportError:
    Document = None

logger = logging.getLogger(__name__)

class ResumeParser:
    """简历解析器"""
    
    def __init__(self):
        self.supported_formats = ['pdf', 'docx', 'doc', 'txt']
        # 数据库字段长度限制 (预留3个字符给"...")
        self.field_limits = {
            'name': 97,    # 100 - 3
            'email': 117,  # 120 - 3  
            'phone': 17    # 20 - 3
        }
        
    def parse_resume(self, file_path: str, file_type: str) -> Dict:
        """
        解析简历文件
        
        Args:
            file_path: 文件路径
            file_type: 文件类型 (pdf, docx, doc)
            
        Returns:
            解析结果字典
        """
        try:
            # 验证文件存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 验证文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise ValueError("文件为空")
            if file_size > 50 * 1024 * 1024:  # 50MB
                raise ValueError("文件过大")
            
            # 提取文本内容
            raw_text = self._extract_text(file_path, file_type)
            
            if not raw_text or len(raw_text.strip()) < 10:
                raise ValueError("无法从文件中提取有效文本内容")
            
            # 解析结构化信息
            parsed_data = self._parse_content_safe(raw_text)
            
            # 验证和清理数据
            validated_data = self._validate_and_clean_data(parsed_data)
            
            return {
                'success': True,
                'raw_text': raw_text,
                'parsed_data': validated_data,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"简历解析失败: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'raw_text': None,
                'parsed_data': None,
                'error': error_msg
            }
    
    def _extract_text(self, file_path: str, file_type: str) -> str:
        """提取文件文本内容"""
        
        if file_type.lower() == 'pdf':
            return self._extract_pdf_text(file_path)
        elif file_type.lower() in ['docx', 'doc']:
            return self._extract_docx_text(file_path)
        elif file_type.lower() == 'txt':
            return self._extract_txt_text(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_type}")
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """提取PDF文本"""
        text = ""
        
        # 首先尝试使用pdfplumber
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text.strip():
                    return text
            except Exception as e:
                logger.warning(f"pdfplumber解析失败: {e}")
        
        # 如果pdfplumber失败，尝试PyPDF2
        if PyPDF2:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except Exception as e:
                logger.warning(f"PyPDF2解析失败: {e}")
        
        raise ValueError("PDF解析库未安装或解析失败")
    
    def _extract_docx_text(self, file_path: str) -> str:
        """提取Word文档文本"""
        if not Document:
            raise ValueError("python-docx库未安装")
        
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Word文档解析失败: {e}")
    
    def _extract_txt_text(self, file_path: str) -> str:
        """提取txt文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text
        except Exception as e:
            raise ValueError(f"txt文件解析失败: {e}")
    
    def _parse_content(self, text: str) -> Dict:
        """解析文本内容，提取结构化信息"""
        
        result = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text)
        }
        
        return result
    
    def _parse_content_safe(self, text: str) -> Dict:
        """安全地解析文本内容，提取结构化信息"""
        result = {
            'name': None,
            'email': None,
            'phone': None,
            'skills': [],
            'experience': [],
            'education': []
        }
        
        # 安全地提取每个字段，单个失败不影响其他字段
        try:
            result['name'] = self._extract_name(text)
        except Exception as e:
            logger.warning(f"姓名提取失败: {e}")
        
        try:
            result['email'] = self._extract_email(text)
        except Exception as e:
            logger.warning(f"邮箱提取失败: {e}")
        
        try:
            result['phone'] = self._extract_phone(text)
        except Exception as e:
            logger.warning(f"电话提取失败: {e}")
        
        try:
            result['skills'] = self._extract_skills(text)
        except Exception as e:
            logger.warning(f"技能提取失败: {e}")
            result['skills'] = []
        
        try:
            result['experience'] = self._extract_experience(text)
        except Exception as e:
            logger.warning(f"工作经历提取失败: {e}")
            result['experience'] = []
        
        try:
            result['education'] = self._extract_education(text)
        except Exception as e:
            logger.warning(f"教育背景提取失败: {e}")
            result['education'] = []
        
        return result
    
    def _validate_and_clean_data(self, data: Dict) -> Dict:
        """验证和清理数据"""
        result = {}
        
        # 处理字符串字段的长度限制
        for field in ['name', 'email', 'phone']:
            value = data.get(field)
            if value and isinstance(value, str):
                limit = self.field_limits.get(field, 100)
                if len(value) > limit:
                    result[field] = value[:limit] + "..."
                else:
                    result[field] = value
            else:
                result[field] = value
        
        # 处理列表字段，确保JSON序列化
        for field in ['skills', 'experience', 'education']:
            value = data.get(field, [])
            result[field] = self._ensure_json_serializable(value)
        
        return result
    
    def _ensure_json_serializable(self, obj):
        """确保对象可以JSON序列化"""
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            if isinstance(obj, list):
                return [str(item) for item in obj if item is not None][:20]  # 限制数量
            elif isinstance(obj, dict):
                return {k: str(v) for k, v in obj.items() if v is not None}
            else:
                return str(obj) if obj is not None else None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """提取姓名"""
        lines = text.split('\n')
        
        # 首先尝试从第一行提取姓名
        if lines:
            first_line = lines[0].strip()
            
            # 从包含联系信息的第一行中提取姓名
            # 匹配格式: "FIRSTNAME LASTNAME (phone) • email • github"
            name_match = re.search(r'^([A-Z][A-Z\s]+?)(?:\s*\(|\s*•|\s*\d)', first_line)
            if name_match:
                name = name_match.group(1).strip()
                if 2 <= len(name.split()) <= 4:  # 验证是合理的姓名
                    return name
            
            # 如果第一行就是纯姓名
            if re.match(r'^[A-Z][A-Z\s]{5,40}$', first_line) and len(first_line.split()) <= 4:
                return first_line
        
        # 通常姓名在简历的前几行
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            if line and len(line) < 50:
                # 排除明显不是姓名的行
                if any(keyword in line.lower() for keyword in 
                      ['email', 'phone', 'tel', '邮箱', '电话', 'address', '地址', 
                       'education', 'experience', 'skills', 'github', '@', 'www', 'http']):
                    continue
                
                # 简单的姓名检测逻辑
                if re.match(r'^[a-zA-Z\u4e00-\u9fff\s]{2,30}$', line):
                    # 如果包含多个单词，可能是姓名
                    words = line.split()
                    if 2 <= len(words) <= 4:  # 通常姓名是2-4个单词
                        return line
                    elif len(words) == 1 and len(line) >= 2:  # 单个中文姓名
                        return line
        
        # 如果前面没找到，尝试从联系信息行中提取
        for line in lines[:10]:
            line = line.strip()
            # 寻找姓名模式，通常在邮箱或电话前面
            name_match = re.search(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)', line)
            if name_match:
                return name_match.group(1)
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """提取邮箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """提取电话号码"""
        # 匹配各种电话号码格式
        phone_patterns = [
            r'\b1[3-9]\d{9}\b',  # 中国手机号
            r'\b\d{3}-\d{4}-\d{4}\b',  # xxx-xxxx-xxxx
            r'\b\d{3}\s\d{4}\s\d{4}\b',  # xxx xxxx xxxx
            r'\(\d{3}\)\s*\d{3}-\d{4}',  # (xxx) xxx-xxxx
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """提取技能 - 安全版本"""
        skills = []
        
        # 技术技能关键词
        tech_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Django', 'Flask',
            'Spring', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', 'Git', 'Linux', 'Machine Learning', 'Deep Learning',
            'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'HTML', 'CSS', 'SQL'
        ]
        
        # 安全地进行关键词匹配
        try:
            text_lower = text.lower()
            for keyword in tech_keywords:
                if keyword.lower() in text_lower:
                    skills.append(keyword)
        except Exception as e:
            logger.warning(f"关键词匹配失败: {e}")
        
        # 安全地寻找技能部分
        try:
            # 使用更简单和安全的正则表达式
            patterns = [
                r'(?:技能|skills?)[:\s]*([^\n]+)',
                r'(?:专业技能|技术技能)[:\s]*([^\n]+)',
                r'(?:核心技能|主要技能)[:\s]*([^\n]+)'
            ]
            
            for pattern in patterns:
                try:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        # 分割技能项
                        skill_items = re.split(r'[,，；;、\|]', match)
                        for item in skill_items:
                            item = item.strip()
                            if item and 2 <= len(item) <= 30:  # 合理的技能长度
                                # 移除常见的项目符号
                                item = re.sub(r'^[•·\-\*\s]+', '', item)
                                if item:
                                    skills.append(item)
                except re.error as e:
                    logger.warning(f"技能正则表达式 {pattern} 失败: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"技能部分解析失败: {e}")
        
        # 去重并限制数量
        unique_skills = list(set(skills))
        return unique_skills[:20]  # 最多返回20个技能
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """提取工作经历"""
        experiences = []
        
        # 寻找工作经历部分
        exp_sections = re.findall(
            r'(?:工作经历|工作经验|职业经历|experience|employment)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|教育|education|技能|skills|$)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        for section in exp_sections:
            # 简单的工作经历解析
            jobs = re.split(r'\n(?=\d{4}|\w+\s+\d{4})', section)
            for job in jobs:
                job = job.strip()
                if job and len(job) > 20:
                    experiences.append({
                        'raw_text': job,
                        'company': self._extract_company_from_job(job),
                        'position': self._extract_position_from_job(job),
                        'duration': self._extract_duration_from_job(job)
                    })
        
        return experiences
    
    def _extract_education(self, text: str) -> List[Dict]:
        """提取教育背景"""
        education = []
        
        # 寻找教育背景部分
        edu_sections = re.findall(
            r'(?:教育背景|教育经历|education|academic)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|工作|experience|技能|skills|$)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        for section in edu_sections:
            schools = re.split(r'\n(?=\d{4}|\w+\s+\d{4})', section)
            for school in schools:
                school = school.strip()
                if school and len(school) > 10:
                    education.append({
                        'raw_text': school,
                        'school': self._extract_school_from_education(school),
                        'degree': self._extract_degree_from_education(school),
                        'duration': self._extract_duration_from_job(school)
                    })
        
        return education
    
    def _extract_company_from_job(self, job_text: str) -> Optional[str]:
        """从工作经历中提取公司名称"""
        lines = job_text.split('\n')
        for line in lines[:2]:  # 通常在前两行
            line = line.strip()
            if line and '公司' in line:
                return line
        return None
    
    def _extract_position_from_job(self, job_text: str) -> Optional[str]:
        """从工作经历中提取职位"""
        # 简单实现，寻找包含职位关键词的行
        position_keywords = ['工程师', '经理', '主管', '总监', '开发', '设计师', 'engineer', 'manager', 'developer']
        lines = job_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in position_keywords):
                return line
        return None
    
    def _extract_duration_from_job(self, text: str) -> Optional[str]:
        """提取时间段"""
        # 匹配时间格式
        duration_patterns = [
            r'\d{4}[年/\-\.]\d{1,2}[月/\-\.]\d{1,2}?\s*[-~至到]\s*\d{4}[年/\-\.]\d{1,2}[月/\-\.]?\d{1,2}?',
            r'\d{4}[年/\-\.]\d{1,2}?\s*[-~至到]\s*\d{4}[年/\-\.]\d{1,2}?',
            r'\d{4}\s*[-~至到]\s*\d{4}',
            r'\d{4}[年/\-\.]\d{1,2}[月/\-\.]\d{1,2}?\s*[-~至到]\s*(?:至今|现在|present)',
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_school_from_education(self, edu_text: str) -> Optional[str]:
        """从教育背景中提取学校名称"""
        lines = edu_text.split('\n')
        for line in lines[:2]:
            line = line.strip()
            if line and ('大学' in line or '学院' in line or 'university' in line.lower() or 'college' in line.lower()):
                return line
        return None
    
    def _extract_degree_from_education(self, edu_text: str) -> Optional[str]:
        """从教育背景中提取学位"""
        degree_keywords = ['学士', '硕士', '博士', 'bachelor', 'master', 'phd', 'doctor', '本科', '研究生']
        lines = edu_text.split('\n')
        for line in lines:
            line = line.strip().lower()
            if any(keyword in line for keyword in degree_keywords):
                return line
        return None 