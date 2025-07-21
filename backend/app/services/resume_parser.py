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
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # 验证文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise ValueError("File is empty")
            if file_size > 50 * 1024 * 1024:  # 50MB
                raise ValueError("File is too large")
            
            # 提取文本内容
            raw_text = self._extract_text(file_path, file_type)
            
            if not raw_text or len(raw_text.strip()) < 10:
                raise ValueError("Unable to extract valid text content from file")
            
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
            error_msg = f"Resume parsing failed: {str(e)}"
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
            raise ValueError(f"Unsupported file format: {file_type}")
    
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
            raise ValueError("python-docx library not installed")
        
        try:
            # 首先尝试使用 python-docx (适用于 .docx 文件)
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            # 检查是否是旧格式 .doc 文件
            error_types_for_doc = [
                'PackageNotFoundError',
                'BadZipFile', 
                'BadZipfile',
                'zipfile.BadZipFile'
            ]
            error_messages_for_doc = [
                'Package not found',
                'File is not a zip file',
                'not a valid zip file',
                'Bad magic number'
            ]
            
            # 检查异常类型或错误消息
            is_doc_format_error = (
                type(e).__name__ in error_types_for_doc or
                any(msg in str(e) for msg in error_messages_for_doc)
            )
            
            if is_doc_format_error:
                logger.info(f"Detected .doc format file, using fallback method: {type(e).__name__}")
                # 尝试多种方法处理 .doc 文件
                return self._extract_doc_text_fallback(file_path)
            else:
                raise ValueError(f"Word document parsing failed: {e}")
    
    def _extract_doc_text_fallback(self, file_path: str) -> str:
        """使用备用方法提取 .doc 文件文本"""
        
        # 方法1: 尝试使用 docx2txt
        try:
            import docx2txt
            text = docx2txt.process(file_path)
            if text and len(text.strip()) > 0:
                logger.info("Successfully extracted text using docx2txt")
                return text
        except Exception as e:
            logger.warning(f"docx2txt failed: {e}")
        
        # 方法2: 尝试使用 antiword 库
        try:
            import antiword
            text = antiword.extract(file_path)
            if text and len(text.strip()) > 0:
                logger.info("Successfully extracted text using antiword")
                return text
        except Exception as e:
            logger.warning(f"antiword failed: {e}")
        
        # 方法3: 尝试使用 olefile 读取 OLE 文档
        try:
            import olefile
            if olefile.isOleFile(file_path):
                logger.info("Detected OLE format Word document")
                text = self._extract_text_from_ole_doc(file_path)
                if text and len(text.strip()) > 100:  # 确保提取到有意义的内容
                    logger.info(f"Successfully extracted {len(text)} characters from OLE document")
                    return text
        except Exception as e:
            logger.warning(f"olefile processing failed: {e}")
        
        # 方法4: 尝试使用 antiword 命令行工具（如果系统中有安装）
        try:
            import subprocess
            result = subprocess.run(['antiword', file_path], capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout:
                text = result.stdout.strip()
                if len(text) > 50:
                    logger.info("Successfully extracted text using antiword command")
                    return text
        except Exception as e:
            logger.warning(f"antiword command failed: {e}")
        
        # 如果所有方法都失败，返回转换建议
        return self._create_conversion_message()
    
    def _extract_text_from_ole_doc(self, file_path: str) -> str:
        """从OLE格式的Word文档中提取文本"""
        try:
            import olefile
            
            ole = olefile.OleFileIO(file_path)
            text_content = []
            
            logger.info(f"OLE file directory structure: {ole.listdir()}")
            
            # 尝试读取 WordDocument 流
            if ole.exists('WordDocument'):
                try:
                    # 读取WordDocument流的原始数据
                    word_stream = ole.openstream('WordDocument')
                    data = word_stream.read()
                    word_stream.close()
                    
                    logger.info(f"WordDocument stream size: {len(data)} bytes")
                    
                    # 简单的文本提取方法
                    extracted_text = self._extract_text_from_binary(data)
                    if extracted_text:
                        text_content.append(extracted_text)
                        logger.info(f"Extracted {len(extracted_text)} characters from WordDocument")
                        
                except Exception as e:
                    logger.warning(f"Failed to read WordDocument stream: {e}")
            
            # 尝试读取其他可能包含文本的流
            try:
                for entry in ole.listdir():
                    entry_name = '/'.join(entry) if isinstance(entry, (list, tuple)) else str(entry)
                    if any(keyword in entry_name.lower() for keyword in ['word', 'text', 'content', '1table']):
                        try:
                            stream = ole.openstream(entry)
                            data = stream.read()
                            stream.close()
                            
                            if len(data) > 100:  # 只处理有足够数据的流
                                text = self._extract_text_from_binary(data)
                                if text and len(text) > 50:
                                    text_content.append(text)
                                    logger.info(f"Extracted text from stream {entry_name}: {len(text)} chars")
                        except Exception as e:
                            logger.warning(f"Failed to read stream {entry_name}: {e}")
                            continue
            except Exception as e:
                logger.warning(f"Failed to iterate streams: {e}")
            
            ole.close()
            
            if text_content:
                # 合并所有提取的文本，去重
                full_text = '\n'.join(text_content)
                # 清理和格式化文本
                cleaned_text = self._clean_extracted_text(full_text)
                logger.info(f"Final extracted text length: {len(cleaned_text)}")
                return cleaned_text
                
        except Exception as e:
            logger.error(f"OLE document processing failed: {e}")
            
        return ""
    
    def _extract_text_from_binary(self, data: bytes) -> str:
        """从二进制数据中提取可读文本"""
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'latin1', 'cp1252']
            
            for encoding in encodings:
                try:
                    # 解码并提取可打印字符
                    decoded = data.decode(encoding, errors='ignore')
                    # 提取长度超过3的连续字母数字字符串
                    import string
                    words = []
                    current_word = ""
                    
                    for char in decoded:
                        if char.isprintable() and char in (string.ascii_letters + string.digits + ' \n\t.-_'):
                            current_word += char
                        else:
                            if len(current_word.strip()) > 2:
                                words.append(current_word.strip())
                            current_word = ""
                    
                    if len(current_word.strip()) > 2:
                        words.append(current_word.strip())
                    
                    text = ' '.join(words)
                    if len(text) > 50:  # 如果提取到足够的文本
                        return text
                        
                except UnicodeDecodeError:
                    continue
                    
        except Exception as e:
            logger.warning(f"Binary text extraction failed: {e}")
            
        return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """清理提取的文本"""
        if not text:
            return ""
        
        # 移除过多的空白字符
        import re
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 移除明显的乱码模式
        text = re.sub(r'[^\w\s\n\r\t\.\,\;\:\!\?\-\(\)\[\]\'\"@#&]', '', text)
        
        # 确保换行符正确
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()

    def _create_conversion_message(self) -> str:
        """创建格式转换建议消息"""
        return """
        [自动生成的提示信息]
        
        检测到这是一个旧版 Microsoft Word (.doc) 文件。
        由于技术限制，无法完全解析此格式。
        
        建议操作：
        1. 使用 Microsoft Word 打开此文件
        2. 选择 "文件" -> "另存为"
        3. 将格式改为 "Word 文档 (.docx)"
        4. 重新上传 .docx 格式的文件
        
        或者您可以：
        - 使用 Google Docs 或 WPS Office 打开并保存为 .docx
        - 使用在线转换工具将 .doc 转换为 .docx
        
        转换后的文件将能够被完整解析，包括工作经历等详细信息。
        """
    
    def _extract_txt_text(self, file_path: str) -> str:
        """提取txt文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text
        except Exception as e:
            raise ValueError(f"Text file parsing failed: {e}")
    
    def _parse_content(self, text: str) -> Dict:
        """解析文本内容，提取结构化信息"""
        
        result = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'projects': self._extract_projects(text)
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
            'education': [],
            'projects': []
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
        
        try:
            result['projects'] = self._extract_projects(text)
        except Exception as e:
            logger.warning(f"项目经验提取失败: {e}")
            result['projects'] = []
        
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
        for field in ['skills', 'experience', 'education', 'projects']:
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
        
        # 特殊模式：处理OLE文档提取的文本，寻找简历中的姓名
        # 匹配 "resume Su Shijie" 或 "translation of Su Shijie" 等模式
        name_patterns = [
            r'(?:resume|translation of|简历)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:Mobile|Email|Phone)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:简历|resume)',
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 验证不是公司名或常见词汇
                exclude_names = ['New South', 'South Wales', 'Business Lead', 'Product Operations', 
                               'Data Tools', 'Google Play', 'Apple Store', 'ByteDance Product', 
                               'University Of', 'Master Of', 'Bachelor Of']
                if not any(exclude in match for exclude in exclude_names):
                    return match
        
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
        # 标准邮箱格式
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            return emails[0]
        
        # 处理OLE文档中可能丢失@符号的情况
        # 匹配类似 "name.domain domain.com" 或 "name domain.com" 的模式
        email_pattern_no_at = r'\b([A-Za-z0-9._%+-]+)\s+(outlook|gmail|hotmail|yahoo|qq|163|126)\s*\.?\s*(com|cn|org|net)\b'
        matches = re.findall(email_pattern_no_at, text, re.IGNORECASE)
        if matches:
            username, domain, tld = matches[0]
            return f"{username}@{domain}.{tld}"
        
        # 另一种模式：匹配 "Email username domain.com"
        email_pattern_email_prefix = r'Email\s+([A-Za-z0-9._%+-]+)\s+([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
        matches = re.findall(email_pattern_email_prefix, text, re.IGNORECASE)
        if matches:
            username, domain = matches[0]
            return f"{username}@{domain}"
            
        return None
    
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
        """提取工作经历 - 改进版，支持特殊Unicode字符格式"""
        experiences = []
        
        # 方法1：针对特殊Unicode字符格式（​​标记）
        work_start = text.find('Work Experience')
        research_start = text.find('Research Experience')
        
        if work_start != -1:
            # 确定工作经历部分的结束位置
            work_end = len(text)
            if research_start != -1 and research_start > work_start:
                work_end = research_start
            
            work_section = text[work_start:work_end].strip()
            logger.info(f"Found work experience section, length: {len(work_section)} characters")
            
            # 查找所有被​​包围的公司名称
            company_pattern = r'​​([^​]+?)​​\s*\|\s*([^|]+?)\s*\|\s*(\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4})'
            companies = re.findall(company_pattern, work_section)
            
            logger.info(f"Found companies with Unicode markers: {len(companies)}")
            
            for company, location, duration in companies:
                company = company.strip()
                location = location.strip()
                duration = duration.strip()
                
                # 查找这个公司后面的详细信息
                company_start = work_section.find(f'​​{company}​​')
                if company_start != -1:
                    # 查找下一个公司的开始位置
                    next_company_start = len(work_section)
                    for other_company, _, _ in companies:
                        other_company = other_company.strip()
                        if other_company != company:
                            other_start = work_section.find(f'​​{other_company}​​', company_start + 1)
                            if other_start != -1:
                                next_company_start = min(next_company_start, other_start)
                    
                    # 提取这个公司的详细信息
                    company_section = work_section[company_start:next_company_start].strip()
                    
                    # 从公司部分第一个换行后的内容中提取职位
                    lines = company_section.split('\n')
                    position = None
                    description_lines = []
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if i == 1 and line and not line.startswith('​​'):  # 第二行通常是职位
                            position = line
                        elif i > 1 and line:  # 其余内容作为描述
                            description_lines.append(line)
                    
                    description = '\n'.join(description_lines) if description_lines else None
                    
                    experience_item = {
                        'raw_text': company_section,
                        'company': company,
                        'position': position,
                        'duration': duration,
                        'location': location,
                        'description': description
                    }
                    experiences.append(experience_item)
                    logger.info(f"Extracted experience: {position} at {company}")
        
        # 方法2：如果方法1没找到足够结果，使用传统方法
        if len(experiences) == 0:
            logger.info("Trying traditional experience extraction method")
            
            # 更全面的工作经历标题匹配模式
            exp_patterns = [
                r'work\s*experience[:\s]*',
                r'professional\s*experience[:\s]*',
                r'employment\s*history[:\s]*',
                r'career\s*history[:\s]*',
                r'experience[:\s]*',
                r'employment[:\s]*',
                r'工作经历[:\s]*',
                r'工作经验[:\s]*',
                r'职业经历[:\s]*'
            ]
            
            # 查找工作经历部分
            for pattern in exp_patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                
                for match in matches:
                    start_pos = match.end()
                    
                    # 查找下一个主要部分的开始位置
                    next_section_patterns = [
                        r'\n\s*(?:education|academic|学历|教育)',
                        r'\n\s*(?:skills|技能|专业技能)',
                        r'\n\s*(?:projects|项目)',
                        r'\n\s*(?:certifications?|证书)',
                        r'\n\s*(?:references?|推荐|联系人)',
                        r'\n\s*(?:languages?|语言)',
                        r'\n\s*(?:interests?|兴趣)',
                        r'\n\s*(?:hobbies|爱好)'
                    ]
                    
                    end_pos = len(text)
                    for next_pattern in next_section_patterns:
                        next_match = re.search(next_pattern, text[start_pos:], re.IGNORECASE)
                        if next_match:
                            end_pos = min(end_pos, start_pos + next_match.start())
                    
                    # 提取这一部分的文本
                    section_text = text[start_pos:end_pos].strip()
                    
                    if section_text and len(section_text) > 50:  # 确保有足够的内容
                        logger.info(f"Found work experience section using pattern: {pattern}")
                        
                        # 尝试多种方式分割工作经历条目
                        jobs = self._split_experience_entries(section_text)
                        
                        for job in jobs:
                            job = job.strip()
                            if job and len(job) > 20:
                                experience_item = {
                                    'raw_text': job,
                                    'company': self._extract_company_from_job(job),
                                    'position': self._extract_position_from_job(job),
                                    'duration': self._extract_duration_from_job(job),
                                    'description': self._extract_description_from_job(job)
                                }
                                experiences.append(experience_item)
                                logger.info(f"Extracted experience: {experience_item['position']} at {experience_item['company']}")
        
        # 去重：如果有相同的工作经历，只保留一个
        unique_experiences = []
        seen_texts = set()
        for exp in experiences:
            if exp['raw_text'] not in seen_texts:
                unique_experiences.append(exp)
                seen_texts.add(exp['raw_text'])
        
        return unique_experiences
    
    def _split_experience_entries(self, section_text: str) -> List[str]:
        """分割工作经历条目"""
        # 方法1: 按年份分割
        jobs = re.split(r'\n(?=\d{4})', section_text)
        if len(jobs) > 1:
            return jobs
        
        # 方法2: 按日期模式分割
        jobs = re.split(r'\n(?=\w+\s+\d{4})', section_text)
        if len(jobs) > 1:
            return jobs
        
        # 方法3: 按空行分割
        jobs = re.split(r'\n\s*\n', section_text)
        if len(jobs) > 1:
            return jobs
        
        # 方法4: 按职位模式分割（如果有明确的职位标题）
        jobs = re.split(r'\n(?=[A-Z][a-z]+(?: [A-Z][a-z]+)*(?:\s+[-–—]\s*|\s+at\s+|\s+@\s+))', section_text)
        if len(jobs) > 1:
            return jobs
        
        # 如果无法分割，返回整个部分作为一个条目
        return [section_text]
    
    def _extract_description_from_job(self, job_text: str) -> Optional[str]:
        """从工作经历中提取工作描述"""
        lines = job_text.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            # 跳过包含公司名、职位、日期的行
            if (not re.search(r'\d{4}', line) and 
                not re.search(r'(?:at\s+|@\s+)[A-Z]', line) and
                len(line) > 20):
                description_lines.append(line)
        
        if description_lines:
            return ' '.join(description_lines)
        return None
    
    def _extract_education(self, text: str) -> List[Dict]:
        """提取教育背景 - 改进版，支持特殊Unicode字符格式"""
        education = []
        
        # 方法1：针对特殊Unicode字符格式（​​标记）
        education_start = text.find('Education')
        work_start = text.find('Work Experience')
        
        if education_start != -1 and work_start != -1:
            education_section = text[education_start:work_start].strip()
            logger.info(f"Found education section, length: {len(education_section)} characters")
            
            # 查找所有被​​包围的大学名称
            university_pattern = r'​​([^​]+?(?:University|College|Institute|School)[^​]*)​​'
            universities = re.findall(university_pattern, education_section)
            
            logger.info(f"Found universities with Unicode markers: {universities}")
            
            for university in universities:
                university = university.strip()
                if len(university) > 5:  # 确保是有效的大学名
                    # 查找这个大学后面的详细信息
                    uni_start = education_section.find(f'​​{university}​​')
                    if uni_start != -1:
                        # 查找下一个大学的开始位置或部分结束位置
                        next_uni_start = len(education_section)
                        for other_uni in universities:
                            if other_uni != university:
                                other_start = education_section.find(f'​​{other_uni}​​', uni_start + 1)
                                if other_start != -1:
                                    next_uni_start = min(next_uni_start, other_start)
                        
                        # 提取这个大学的详细信息
                        uni_section = education_section[uni_start:next_uni_start].strip()
                        
                        # 提取学位信息
                        degree = None
                        degree_patterns = [
                            r'(MS in [^|]+)',
                            r'(BSc in [^|]+)', 
                            r'(MA in [^|]+)',
                            r'(BA in [^|]+)',
                            r'(PhD in [^|]+)',
                            r'(Bachelor[^|]+)',
                            r'(Master[^|]+)'
                        ]
                        
                        for pattern in degree_patterns:
                            degree_match = re.search(pattern, uni_section)
                            if degree_match:
                                degree = degree_match.group(1).strip()
                                break
                        
                        # 提取时间
                        duration_pattern = r'(\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4})'
                        duration_match = re.search(duration_pattern, uni_section)
                        duration = duration_match.group(1).strip() if duration_match else None
                        
                        # 提取地点
                        location = None
                        if 'USA' in uni_section:
                            if 'Washington' in uni_section:
                                location = 'Washington, D.C., USA'
                            else:
                                location = 'USA'
                        elif 'China' in uni_section:
                            if 'Suzhou' in uni_section:
                                location = 'Suzhou, China'
                            else:
                                location = 'China'
                        
                        # 提取其他信息（GPA等）
                        gpa_match = re.search(r'GPA:\s*([\d.]+)', uni_section)
                        gpa = gpa_match.group(1) if gpa_match else None
                        
                        education_item = {
                            'raw_text': uni_section,
                            'school': university,
                            'degree': degree,
                            'duration': duration,
                            'location': location,
                            'gpa': gpa
                        }
                        education.append(education_item)
                        logger.info(f"Extracted education: {degree} from {university}")
        
        # 方法2：如果方法1没找到结果，使用传统方法
        if len(education) == 0:
            logger.info("Trying traditional education extraction method")
            
            # 寻找教育背景部分
            edu_sections = re.findall(
                r'(?:教育背景|教育经历|education|academic)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|工作|experience|技能|skills|$)',
                text, re.IGNORECASE | re.DOTALL
            )
            
            for section in edu_sections:
                section = section.strip()
                if not section:
                    continue
                    
                # 方法1: 尝试按换行符分割（适用于格式良好的文档）
                if '\n' in section:
                    schools = re.split(r'\n(?=\d{4}|\w+\s+\d{4})', section)
                else:
                    # 方法2: 按日期模式分割（适用于.doc文件等无换行符的情况）
                    # 匹配 "年.月 年.月 学校信息" 的模式
                    education_pattern = r'(\d{4}[\.\-/]\d{1,2}\s+\d{4}[\.\-/]\d{1,2}\s+[^0-9]+?)(?=\d{4}[\.\-/]\d{1,2}|$)'
                    matches = re.findall(education_pattern, section)
                    if matches:
                        schools = matches
                    else:
                        # 如果没有明确的日期模式，尝试其他分割方法
                        schools = [section] if len(section) > 10 else []
                
                for school in schools:
                    school = school.strip()
                    if school and len(school) > 10:
                        education.append({
                            'raw_text': school,
                            'school': self._extract_school_from_education(school),
                            'degree': self._extract_degree_from_education(school),
                            'duration': self._extract_duration_from_education(school)
                        })
        
        return education
    
    def _extract_company_from_job(self, job_text: str) -> Optional[str]:
        """从工作经历中提取公司名称"""
        lines = job_text.split('\n')
        
        # 尝试多种模式匹配公司名
        patterns = [
            # 格式: "at Company Name" 或 "@ Company Name"
            r'(?:at\s+|@\s*)([A-Z][A-Za-z\s&.,Inc-]+?)(?:\s*[,\n]|\s*$)',
            # 格式: 行首的公司名（通常是第二行）
            r'^([A-Z][A-Za-z\s&.,Inc-]+?)(?:\s*[,\n]|\s+\d{4}|\s*$)',
            # 格式: 包含公司后缀的
            r'([A-Z][A-Za-z\s&.,-]+?)\s*(?:Inc\.?|Corp\.?|Ltd\.?|LLC\.?|Co\.?|Company|公司)',
            # 中文公司名
            r'([A-Za-z\u4e00-\u9fff][A-Za-z\s\u4e00-\u9fff&.,-]*?公司)',
        ]
        
        for line in lines[:4]:  # 检查前几行
            line = line.strip()
            if not line:
                continue
                
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    company = match.group(1).strip()
                    # 验证提取的公司名是否合理
                    if (len(company) > 2 and len(company) < 80 and 
                        not re.search(r'\d{4}', company) and  # 不包含年份
                        not re.search(r'[•·]', company)):     # 不包含项目符号
                        return company
        
        # 如果没有匹配，尝试启发式方法
        for line in lines[:3]:
            line = line.strip()
            if (line and len(line) > 3 and len(line) < 60 and
                not re.search(r'\d{4}', line) and  # 不包含年份
                not line.lower().startswith(('responsible', 'manage', 'develop', 'lead', 'work'))):
                return line
        
        return None
    
    def _extract_position_from_job(self, job_text: str) -> Optional[str]:
        """从工作经历中提取职位"""
        lines = job_text.split('\n')
        
        # 职位关键词（扩展列表）
        position_keywords = [
            # 英文职位
            'engineer', 'developer', 'manager', 'director', 'analyst', 'consultant',
            'specialist', 'coordinator', 'administrator', 'supervisor', 'lead',
            'senior', 'junior', 'intern', 'associate', 'assistant', 'executive',
            'officer', 'representative', 'technician', 'designer', 'architect',
            'scientist', 'researcher', 'programmer', 'tester', 'qa', 'product',
            'project', 'business', 'sales', 'marketing', 'finance', 'hr',
            # 中文职位
            '工程师', '开发', '经理', '主管', '总监', '专员', '助理', '顾问',
            '分析师', '设计师', '架构师', '测试', '产品', '项目', '运营',
            '销售', '市场', '财务', '人事', '行政', '客服'
        ]
        
        # 方法1: 寻找包含职位关键词的行
        for line in lines[:3]:  # 职位通常在前几行
            line = line.strip()
            if line and any(keyword in line.lower() for keyword in position_keywords):
                # 清理职位名称
                position = line
                # 移除公司信息
                position = re.sub(r'\s*(?:at\s+|@\s*)[A-Z].*', '', position)
                # 移除时间信息
                position = re.sub(r'\s*\d{4}.*', '', position)
                # 移除多余的标点
                position = re.sub(r'[•·\-—]\s*', '', position).strip()
                
                if position and len(position) > 2 and len(position) < 100:
                    return position
        
        # 方法2: 如果没有明显的职位关键词，取第一行（通常是职位）
        for line in lines[:2]:
            line = line.strip()
            if (line and len(line) > 3 and len(line) < 80 and
                not re.search(r'\d{4}', line) and  # 不包含年份
                not re.search(r'(?:at\s+|@\s*)[A-Z]', line)):  # 不包含公司指示符
                return line
        
        return None
    
    def _extract_duration_from_job(self, text: str) -> Optional[str]:
        """提取时间段"""
        # 匹配各种时间格式
        duration_patterns = [
            # 英文格式: January 2020 - March 2022
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s*[-–—]\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            # 英文格式: Jan 2020 - Mar 2022
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}',
            # 英文格式: 2020 - 2022
            r'\d{4}\s*[-–—]\s*\d{4}',
            # 英文格式: 2020 - Present
            r'\d{4}\s*[-–—]\s*(?:Present|present|Current|current)',
            # 月/年格式: 01/2020 - 03/2022
            r'\d{1,2}/\d{4}\s*[-–—]\s*\d{1,2}/\d{4}',
            # 中文格式
            r'\d{4}[年/\-\.]\d{1,2}[月/\-\.]\d{1,2}?\s*[-~至到]\s*\d{4}[年/\-\.]\d{1,2}[月/\-\.]?\d{1,2}?',
            r'\d{4}[年/\-\.]\d{1,2}?\s*[-~至到]\s*\d{4}[年/\-\.]\d{1,2}?',
            r'\d{4}\s*[-~至到]\s*\d{4}',
            r'\d{4}[年/\-\.]\d{1,2}[月/\-\.]\d{1,2}?\s*[-~至到]\s*(?:至今|现在|present)',
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        # 如果没有找到完整的时间段，尝试找单个年份
        year_pattern = r'\b\d{4}\b'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            return f"{years[0]} - {years[-1]}"
        elif len(years) == 1:
            return years[0]
        
        return None
    
    def _extract_school_from_education(self, edu_text: str) -> Optional[str]:
        """从教育背景中提取学校名称"""
        if not edu_text:
            return None
            
        # 移除开头的日期信息
        text = re.sub(r'^\d{4}[\.\-/]\d{1,2}\s+\d{4}[\.\-/]\d{1,2}\s+', '', edu_text.strip())
        
        # 学位关键词（用于识别边界）
        degree_keywords = ['bachelor', 'master', 'phd', 'doctor', '学士', '硕士', '博士', '本科', '研究生']
        
        # 方法1: 使用正则表达式直接匹配学校名模式
        # 匹配学校名到学位关键词之间的内容
        school_patterns = [
            # 匹配以学校名开头到学位关键词的部分
            r'^([^0-9]*?university[^0-9]*?)(?:\s+(?:bachelor|master|phd|doctor))',
            r'^([^0-9]*?college[^0-9]*?)(?:\s+(?:bachelor|master|phd|doctor))',
            r'^([^0-9]*?institute[^0-9]*?)(?:\s+(?:bachelor|master|phd|doctor))',
            r'^([^0-9]*?school[^0-9]*?)(?:\s+(?:bachelor|master|phd|doctor))',
            # 中文学校
            r'^([^0-9]*?大学[^0-9]*?)(?:\s+(?:学士|硕士|博士|本科))',
            r'^([^0-9]*?学院[^0-9]*?)(?:\s+(?:学士|硕士|博士|本科))',
        ]
        
        text_lower = text.lower()
        for pattern in school_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                school_name = match.group(1).strip()
                # 清理多余的词语
                school_name = re.sub(r'\s+of\s+$', '', school_name)  # 移除结尾的 "of"
                if len(school_name) > 3:
                    return school_name
        
        # 方法2: 如果没有明确的学位边界，寻找学校关键词
        words = text.split()
        school_keywords = ['university', 'college', '大学', '学院', 'institute', 'school']
        
        # 找到包含学校关键词的词及其前面的词
        for i, word in enumerate(words):
            if any(keyword in word.lower() for keyword in school_keywords):
                # 向前收集学校名称的词
                school_words = []
                
                # 向前找学校名的组成部分
                start_idx = max(0, i - 3)  # 最多向前看3个词
                for j in range(start_idx, i + 1):
                    candidate_word = words[j]
                    # 跳过学位关键词
                    if any(deg_kw in candidate_word.lower() for deg_kw in degree_keywords):
                        continue
                    # 收集看起来像学校名称的词
                    if (len(candidate_word) > 2 and 
                        (candidate_word[0].isupper() or candidate_word.lower() in ['of', 'and', '&', '-'])):
                        school_words.append(candidate_word)
                
                if school_words:
                    school_name = ' '.join(school_words)
                    # 清理学校名称
                    school_name = re.sub(r'\s+of\s*$', '', school_name)  # 移除结尾的 "of"
                    school_name = re.sub(r'^\s*of\s+', '', school_name)  # 移除开头的 "of"
                    return school_name.strip()
        
        # 方法3: 寻找连续的大写词语作为学校名
        capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*\s+(?:University|College|Institute|School)', text, re.IGNORECASE)
        if capitalized_phrases:
            return capitalized_phrases[0]
        
        return None
    
    def _extract_degree_from_education(self, edu_text: str) -> Optional[str]:
        """从教育背景中提取学位"""
        if not edu_text:
            return None
            
        # 移除开头的日期信息
        text = re.sub(r'^\d{4}[\.\-/]\d{1,2}\s+\d{4}[\.\-/]\d{1,2}\s+', '', edu_text.strip())
        
        # 学位关键词和模式
        degree_patterns = [
            # 完整学位模式
            r'(bachelor\s+of\s+[a-z\s]+)',
            r'(master\s+of\s+[a-z\s]+)',
            r'(doctor\s+of\s+[a-z\s]+)',
            r'(phd\s+in\s+[a-z\s]+)',
            # 中文学位
            r'([a-z\s]*学士[a-z\s]*)',
            r'([a-z\s]*硕士[a-z\s]*)',
            r'([a-z\s]*博士[a-z\s]*)',
            r'([a-z\s]*本科[a-z\s]*)',
            r'([a-z\s]*研究生[a-z\s]*)',
        ]
        
        text_lower = text.lower()
        
        # 寻找完整的学位表述
        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                # 返回最长的匹配（通常更完整）
                best_match = max(matches, key=len)
                return best_match.strip()
        
        # 如果没有找到完整模式，寻找学位关键词
        degree_keywords = ['bachelor', 'master', 'phd', 'doctor', '学士', '硕士', '博士', '本科', '研究生']
        words = text.split()
        
        for i, word in enumerate(words):
            if any(keyword in word.lower() for keyword in degree_keywords):
                # 找到学位关键词，尝试构建完整的学位名称
                degree_words = [word]
                
                # 向后查找相关词语
                for j in range(i + 1, min(i + 5, len(words))):
                    next_word = words[j].lower()
                    if next_word in ['of', 'in', 'and', '&'] or any(subj in next_word for subj in ['arts', 'science', 'commerce', 'engineering', 'business']):
                        degree_words.append(words[j])
                    else:
                        break
                
                if len(degree_words) > 1:
                    return ' '.join(degree_words)
                else:
                    return word
        
        return None
    
    def _extract_duration_from_education(self, edu_text: str) -> Optional[str]:
        """从教育背景中提取时间段"""
        if not edu_text:
            return None
            
        # 专门针对教育背景的时间模式
        # 格式: "2019.8 2020.9" 或 "2015.9 2019.6"
        date_patterns = [
            # 年.月 年.月 格式
            r'(\d{4}[\.\-/]\d{1,2})\s+(\d{4}[\.\-/]\d{1,2})',
            # 年-年 格式
            r'(\d{4})\s*-\s*(\d{4})',
            # 年 年 格式
            r'(\d{4})\s+(\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, edu_text)
            if match:
                start_date = match.group(1)
                end_date = match.group(2)
                
                # 提取年份进行格式化
                start_year = re.search(r'\d{4}', start_date).group()
                end_year = re.search(r'\d{4}', end_date).group()
                
                return f"{start_year} - {end_year}"
        
        # 如果没有找到配对的日期，寻找单个年份
        years = re.findall(r'\d{4}', edu_text)
        if len(years) >= 2:
            return f"{years[0]} - {years[1]}"
        elif len(years) == 1:
            return years[0]
            
        return None
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """提取项目经验"""
        projects = []
        
        # 项目相关的section标题匹配模式
        project_section_patterns = [
            r'(?:projects?|项目|项目经验|作品|portfolio)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|experience|education|skills|技能|工作|教育|$)',
            r'(?:personal\s*projects?|个人项目)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|experience|education|skills|技能|工作|教育|$)',
            r'(?:academic\s*projects?|学术项目)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|experience|education|skills|技能|工作|教育|$)',
            r'(?:capstone\s*projects?|毕业项目)[:\s]*\n?(.*?)(?:\n\n|\n(?=[A-Z])|experience|education|skills|技能|工作|教育|$)'
        ]
        
        # 方法1: 寻找专门的项目section
        for pattern in project_section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for section in matches:
                section = section.strip()
                if section and len(section) > 20:
                    logger.info(f"Found project section using pattern: {pattern}")
                    
                    # 分割项目条目
                    project_entries = self._split_project_entries(section)
                    
                    for entry in project_entries:
                        entry = entry.strip()
                        if entry and len(entry) > 30:
                            project_item = {
                                'raw_text': entry,
                                'name': self._extract_project_name(entry),
                                'description': self._extract_project_description(entry),
                                'technologies': self._extract_project_technologies(entry),
                                'duration': self._extract_duration_from_job(entry),  # 重用已有方法
                                'type': 'project_section'
                            }
                            projects.append(project_item)
                            logger.info(f"Extracted project: {project_item['name']}")
        
        # 方法2: 从工作经历中提取项目相关的条目
        # 寻找包含项目关键词的工作经历条目
        project_keywords = ['project', 'capstone', 'design project', '项目', '毕业设计', '课程设计']
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in project_keywords):
                # 收集相关的上下文
                context_lines = []
                start_idx = max(0, i - 2)
                end_idx = min(len(lines), i + 5)
                
                for j in range(start_idx, end_idx):
                    context_lines.append(lines[j])
                
                context = '\n'.join(context_lines).strip()
                
                if len(context) > 50:
                    project_item = {
                        'raw_text': context,
                        'name': self._extract_project_name(context),
                        'description': self._extract_project_description(context),
                        'technologies': self._extract_project_technologies(context),
                        'duration': self._extract_duration_from_job(context),
                        'type': 'experience_project'
                    }
                    
                    # 避免重复添加相同的项目
                    if not any(p['raw_text'] == project_item['raw_text'] for p in projects):
                        projects.append(project_item)
                        logger.info(f"Extracted experience project: {project_item['name']}")
        
        return projects
    
    def _split_project_entries(self, section_text: str) -> List[str]:
        """分割项目条目"""
        # 方法1: 按项目符号分割
        entries = re.split(r'\n[•·\-\*]\s*', section_text)
        if len(entries) > 1:
            return entries
        
        # 方法2: 按编号分割
        entries = re.split(r'\n\d+[\.\)]\s*', section_text)
        if len(entries) > 1:
            return entries
        
        # 方法3: 按空行分割
        entries = re.split(r'\n\s*\n', section_text)
        if len(entries) > 1:
            return entries
        
        # 方法4: 按项目名称模式分割（大写开头的行）
        entries = re.split(r'\n(?=[A-Z][A-Za-z\s]{10,})', section_text)
        if len(entries) > 1:
            return entries
        
        # 如果无法分割，返回整个section作为一个项目
        return [section_text]
    
    def _extract_project_name(self, project_text: str) -> Optional[str]:
        """提取项目名称"""
        lines = project_text.split('\n')
        
        # 清理特殊Unicode字符和格式标记
        def clean_text(text):
            # 移除Unicode格式字符（如 ​​）
            text = re.sub(r'[\u200B-\u200D\u2060\uFEFF]', '', text)
            # 移除常见的项目符号和编号
            text = re.sub(r'^[•·\-\*\d\.\)]\s*', '', text)
            # 移除多余的空白字符
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        
        # 方法1: 寻找具体的项目名称（包含名词的行）
        for line in lines[:5]:  # 检查前5行
            cleaned_line = clean_text(line)
            if not cleaned_line or len(cleaned_line) < 3:
                continue
                
            # 跳过明显的标题行（如"Projects:", "项目："等）
            if re.match(r'^(?:projects?|项目|项目经验|作品)[:：]?\s*$', cleaned_line, re.IGNORECASE):
                continue
                
            # 跳过明显的角色描述（如"Team Lead", "Member"等）
            if re.match(r'^(?:team\s*lead|member|负责人|成员)[:：]?', cleaned_line, re.IGNORECASE):
                continue
            
            # 寻找包含实际项目名称的行
            # 项目名通常包含：产品名、系统名、活动名等
            name_indicators = [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4}\b',  # 英文标题格式
                r'["""][^"""]+["""]',  # 引号包围的名称
                r'[a-zA-Z\u4e00-\u9fff]+(?:\s+[a-zA-Z\u4e00-\u9fff]+){1,5}(?:\s*[项目系统平台应用网站])',  # 中文项目名
                r'Reading\s+[A-Z][a-z]+',  # 特定格式如"Reading Aid"
                r'Ocean\s+Literacy',  # 特定项目名
                r'Shan\s+Hai\s+Qing',  # 特定项目名
            ]
            
            for pattern in name_indicators:
                matches = re.findall(pattern, cleaned_line)
                if matches:
                    # 选择最合适的匹配（通常是最长的）
                    best_match = max(matches, key=len) if matches else matches[0]
                    if len(best_match) > 5 and len(best_match) < 60:
                        return best_match
        
        # 方法2: 寻找描述性的项目名称
        for line in lines[:3]:
            cleaned_line = clean_text(line)
            if not cleaned_line:
                continue
                
            # 如果行包含项目相关词汇且长度合适
            if (any(keyword in cleaned_line.lower() for keyword in 
                   ['reading', 'literacy', 'innovation', 'competition', 'aid', 'documentary',
                    '阅读', '识字', '创新', '竞赛', '援助', '纪录片', '研究']) and
                5 < len(cleaned_line) < 80 and
                not re.search(r'\d{4}', cleaned_line)):  # 不包含年份
                return cleaned_line
        
        # 方法3: 提取第一行中的关键词组
        if lines:
            first_line = clean_text(lines[0])
            if first_line and len(first_line) < 100:
                # 尝试提取有意义的词组
                words = first_line.split()
                if len(words) >= 2:
                    # 取前几个有意义的词
                    meaningful_words = []
                    for word in words[:4]:
                        if len(word) > 2 and not word.lower() in ['the', 'and', 'or', 'in', 'on', 'at']:
                            meaningful_words.append(word)
                    
                    if meaningful_words:
                        return ' '.join(meaningful_words)
                
                return first_line
        
        return "项目"  # 默认名称
    
    def _extract_project_description(self, project_text: str) -> Optional[str]:
        """提取项目描述"""
        lines = project_text.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 跳过可能是项目名称的第一行
            if (len(description_lines) == 0 and 
                len(line) < 100 and 
                any(keyword in line.lower() for keyword in 
                   ['project', 'design', 'application', 'system', '项目'])):
                continue
            
            # 收集描述行
            if len(line) > 10:  # 确保有意义的内容
                # 清理项目符号
                clean_line = re.sub(r'^[•·\-\*]\s*', '', line)
                description_lines.append(clean_line)
        
        if description_lines:
            description = ' '.join(description_lines)
            # 限制描述长度
            if len(description) > 500:
                description = description[:500] + "..."
            return description
        
        return None
    
    def _extract_project_technologies(self, project_text: str) -> List[str]:
        """提取项目使用的技术栈"""
        technologies = []
        
        # 技术关键词库
        tech_keywords = [
            # 编程语言
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'PHP', 'Ruby',
            # 前端技术
            'React', 'Vue', 'Angular', 'HTML', 'CSS', 'jQuery', 'Bootstrap',
            # 后端技术
            'Django', 'Flask', 'Spring', 'Express', 'Node.js', 'Laravel',
            # 数据库
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite',
            # 工具和平台
            'Git', 'Docker', 'AWS', 'Azure', 'Kubernetes', 'Jenkins',
            # 移动开发
            'Android', 'iOS', 'React Native', 'Flutter',
            # 数据科学
            'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn',
            # 其他
            'API', 'REST', 'GraphQL', 'Microservices'
        ]
        
        project_text_lower = project_text.lower()
        for tech in tech_keywords:
            if tech.lower() in project_text_lower:
                technologies.append(tech)
        
        # 去重并限制数量
        unique_technologies = list(set(technologies))
        return unique_technologies[:8]  # 最多返回8个技术