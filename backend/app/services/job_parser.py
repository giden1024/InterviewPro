import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class JobParser:
    """职位信息解析器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def parse_job_url(self, url: str) -> Dict:
        """解析职位URL"""
        try:
            # 验证URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {'success': False, 'error': 'Invalid URL format'}
            
            # 获取网页内容
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取职位信息
            job_data = self._extract_job_info(soup, url)
            
            return {
                'success': True,
                'data': job_data,
                'source_url': url
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch job URL {url}: {e}")
            return {'success': False, 'error': f'Failed to fetch URL: {str(e)}'}
        except Exception as e:
            logger.error(f"Failed to parse job URL {url}: {e}")
            return {'success': False, 'error': f'Parsing failed: {str(e)}'}
    
    def _extract_job_info(self, soup: BeautifulSoup, url: str) -> Dict:
        """从HTML中提取职位信息"""
        job_data = {
            'title': '',
            'company': '',
            'description': '',
            'requirements': [],
            'responsibilities': [],
            'location': '',
            'salary_range': '',
            'job_type': 'full-time',
            'skills_required': [],
            'experience_level': '',
            'parsed_data': {}
        }
        
        # 尝试不同的选择器提取标题
        title_selectors = [
            'h1[data-automation="job-detail-title"]',  # SEEK
            '.jobsearch-JobInfoHeader-title',  # Indeed
            'h1.job-title',
            'h1[class*="title"]',
            'h1[class*="job"]',
            'h1',
            '.job-header h1',
            '[data-testid="job-title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                job_data['title'] = title_elem.get_text(strip=True)
                break
        
        # 提取公司名称
        company_selectors = [
            '[data-automation="job-detail-company"]',
            '.jobsearch-InlineCompanyRating a',
            '.company-name',
            '[class*="company"]',
            '[data-testid="company-name"]'
        ]
        
        for selector in company_selectors:
            company_elem = soup.select_one(selector)
            if company_elem:
                job_data['company'] = company_elem.get_text(strip=True)
                break
        
        # 提取描述
        desc_selectors = [
            '[data-automation="job-detail-description"]',
            '#jobDescriptionText',
            '.job-description',
            '[class*="description"]',
            '.content'
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                job_data['description'] = desc_elem.get_text(strip=True)
                break
        
        # 提取位置
        location_selectors = [
            '[data-automation="job-detail-location"]',
            '.jobsearch-JobInfoHeader-subtitle',
            '.location',
            '[class*="location"]'
        ]
        
        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem:
                job_data['location'] = location_elem.get_text(strip=True)
                break
        
        # 从描述中提取技能和要求
        if job_data['description']:
            job_data['skills_required'] = self._extract_skills(job_data['description'])
            job_data['requirements'] = self._extract_requirements(job_data['description'])
            job_data['experience_level'] = self._extract_experience_level(job_data['description'])
        
        # 存储原始解析数据
        job_data['parsed_data'] = {
            'source_url': url,
            'parsing_method': 'web_scraping',
            'raw_html_title': soup.title.string if soup.title else '',
            'meta_description': self._get_meta_description(soup)
        }
        
        return job_data
    
    def _extract_skills(self, text: str) -> List[str]:
        """从文本中提取技能关键词"""
        # 常见技能关键词
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|TypeScript|React|Vue|Angular|Node\.js|Django|Flask|Spring|Laravel)\b',
            r'\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub)\b',
            r'\b(?:HTML|CSS|SASS|LESS|Bootstrap|Tailwind)\b',
            r'\b(?:Machine Learning|AI|Data Science|Analytics|Statistics)\b',
            r'\b(?:Agile|Scrum|DevOps|CI/CD|TDD|BDD)\b'
        ]
        
        skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend([match for match in matches if match not in skills])
        
        return skills[:10]  # 限制数量
    
    def _extract_requirements(self, text: str) -> List[str]:
        """从文本中提取职位要求"""
        requirements = []
        
        # 查找要求相关的段落
        requirement_patterns = [
            r'(?:Requirements?|Qualifications?|Must have|Essential|Mandatory)[:\s]*([^\.]+)',
            r'(?:You will need|We require|Looking for)[:\s]*([^\.]+)',
            r'(?:Experience with|Knowledge of|Proficiency in)[:\s]*([^\.]+)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.strip()) > 10:  # 过滤太短的匹配
                    requirements.append(match.strip())
        
        return requirements[:5]  # 限制数量
    
    def _extract_experience_level(self, text: str) -> str:
        """从文本中提取经验要求"""
        experience_patterns = [
            (r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', 'years'),
            (r'entry.level|junior|graduate|intern', 'entry'),
            (r'senior|lead|principal|architect', 'senior'),
            (r'mid.level|intermediate', 'mid')
        ]
        
        for pattern, level in experience_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if level == 'years':
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        years = int(match.group(1))
                        if years <= 2:
                            return 'entry'
                        elif years <= 5:
                            return 'mid'
                        else:
                            return 'senior'
                return level
        
        return 'not_specified'
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """获取页面meta描述"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        return ''
    
    def parse_job_text(self, job_text: str, title: str = '', company: str = '') -> Dict:
        """解析职位描述文本"""
        try:
            job_data = {
                'title': title,
                'company': company,
                'description': job_text,
                'requirements': self._extract_requirements(job_text),
                'responsibilities': self._extract_responsibilities(job_text),
                'skills_required': self._extract_skills(job_text),
                'experience_level': self._extract_experience_level(job_text),
                'location': self._extract_location(job_text),
                'salary_range': self._extract_salary(job_text),
                'job_type': self._extract_job_type(job_text),
                'parsed_data': {
                    'parsing_method': 'text_analysis',
                    'text_length': len(job_text)
                }
            }
            
            return {
                'success': True,
                'data': job_data
            }
            
        except Exception as e:
            logger.error(f"Failed to parse job text: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """从文本中提取工作职责"""
        responsibilities = []
        
        responsibility_patterns = [
            r'(?:Responsibilities?|Duties|You will|Role includes)[:\s]*([^\.]+)',
            r'(?:Key responsibilities|Main duties|Primary tasks)[:\s]*([^\.]+)'
        ]
        
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.strip()) > 10:
                    responsibilities.append(match.strip())
        
        return responsibilities[:5]
    
    def _extract_location(self, text: str) -> str:
        """从文本中提取位置信息"""
        location_patterns = [
            r'(?:Location|Based in|Office)[:\s]*([A-Za-z\s,]+)',
            r'(?:Remote|Work from home|WFH)',
            r'(?:Hybrid|Flexible working)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'Remote' in match.group(0):
                    return 'Remote'
                elif 'Hybrid' in match.group(0):
                    return 'Hybrid'
                else:
                    return match.group(1).strip() if match.groups() else match.group(0)
        
        return ''
    
    def _extract_salary(self, text: str) -> str:
        """从文本中提取薪资信息"""
        salary_patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',
            r'[\d,]+k\s*-\s*[\d,]+k',
            r'Salary[:\s]*\$?[\d,]+',
            r'Up to \$?[\d,]+'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ''
    
    def _extract_job_type(self, text: str) -> str:
        """从文本中提取工作类型"""
        if re.search(r'part.time|part time', text, re.IGNORECASE):
            return 'part-time'
        elif re.search(r'contract|contractor|freelance', text, re.IGNORECASE):
            return 'contract'
        elif re.search(r'intern|internship', text, re.IGNORECASE):
            return 'internship'
        else:
            return 'full-time' 