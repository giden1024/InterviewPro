"""
Resume Analyzer Service
智能简历分析服务，提供简历质量评估、技能分析、改进建议等功能
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from collections import Counter

class ResumeAnalyzer:
    """简历分析器"""
    
    def __init__(self):
        # 技能关键词库
        self.skill_categories = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'bash', 'powershell'
            ],
            'frameworks': [
                'react', 'vue', 'angular', 'flask', 'django', 'spring', 'express', 'fastapi',
                'laravel', 'rails', 'asp.net', 'node.js', 'next.js', 'nuxt.js', 'svelte'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite',
                'cassandra', 'dynamodb', 'neo4j', 'influxdb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'alibaba cloud', 'docker', 'kubernetes', 'terraform',
                'cloudformation', 'ansible', 'jenkins', 'gitlab ci'
            ],
            'ai_ml': [
                'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'opencv', 'nlp',
                'deep learning', 'machine learning', 'data science', 'computer vision'
            ],
            'tools': [
                'git', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'figma', 'adobe',
                'postman', 'swagger', 'linux', 'windows', 'macos'
            ]
        }
        
        # 经验级别关键词
        self.experience_keywords = {
            'junior': ['junior', 'entry', 'intern', 'trainee', 'assistant', '实习', '初级'],
            'mid': ['developer', 'engineer', 'analyst', 'specialist', '开发', '工程师'],
            'senior': ['senior', 'lead', 'principal', 'architect', 'manager', '高级', '资深', '主管'],
            'executive': ['director', 'vp', 'cto', 'ceo', 'head', '总监', '副总', '总裁']
        }
        
        # 教育关键词
        self.education_keywords = {
            'degree_types': ['bachelor', 'master', 'phd', 'doctorate', '学士', '硕士', '博士'],
            'fields': ['computer science', 'software engineering', 'data science', 'mathematics',
                      'engineering', 'business', '计算机', '软件', '数据', '数学', '工程', '商科']
        }
    
    def analyze_resume(self, resume) -> Dict:
        """
        全面分析简历
        
        Args:
            resume: Resume模型实例
            
        Returns:
            分析结果字典
        """
        analysis = {
            'overall_score': 0,
            'sections': {},
            'skills_analysis': {},
            'experience_analysis': {},
            'education_analysis': {},
            'suggestions': [],
            'strengths': [],
            'weaknesses': [],
            'analysis_date': datetime.utcnow().isoformat()
        }
        
        try:
            # 基本信息分析
            analysis['sections']['basic_info'] = self._analyze_basic_info(resume)
            
            # 技能分析
            analysis['skills_analysis'] = self._analyze_skills(resume.skills or [])
            analysis['sections']['skills'] = self._score_skills_section(resume.skills or [])
            
            # 工作经验分析
            analysis['experience_analysis'] = self._analyze_experience(resume.experience or [])
            analysis['sections']['experience'] = self._score_experience_section(resume.experience or [])
            
            # 教育背景分析
            analysis['education_analysis'] = self._analyze_education(resume.education or [])
            analysis['sections']['education'] = self._score_education_section(resume.education or [])
            
            # 内容质量分析
            analysis['sections']['content_quality'] = self._analyze_content_quality(resume.raw_text or '')
            
            # 生成建议和总结
            analysis['suggestions'] = self._generate_suggestions(analysis)
            analysis['strengths'] = self._identify_strengths(analysis)
            analysis['weaknesses'] = self._identify_weaknesses(analysis)
            
            # 计算总分
            analysis['overall_score'] = self._calculate_overall_score(analysis['sections'])
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_basic_info(self, resume) -> Dict:
        """分析基本信息完整性"""
        score = 0
        details = {}
        
        # 检查姓名
        if resume.name:
            score += 20
            details['name'] = {'present': True, 'score': 20}
        else:
            details['name'] = {'present': False, 'score': 0}
        
        # 检查邮箱
        if resume.email and self._is_valid_email(resume.email):
            score += 25
            details['email'] = {'present': True, 'valid': True, 'score': 25}
        else:
            details['email'] = {'present': bool(resume.email), 'valid': False, 'score': 0}
        
        # 检查电话
        if resume.phone:
            score += 20
            details['phone'] = {'present': True, 'score': 20}
        else:
            details['phone'] = {'present': False, 'score': 0}
        
        return {
            'score': score,
            'max_score': 65,
            'percentage': round((score / 65) * 100, 1),
            'details': details
        }
    
    def _analyze_skills(self, skills: List[str]) -> Dict:
        """技能分析"""
        if not skills:
            return {'total_skills': 0, 'categories': {}, 'recommendations': []}
        
        skills_lower = [skill.lower() for skill in skills]
        categories = {}
        
        # 按类别分类技能
        for category, keywords in self.skill_categories.items():
            found_skills = []
            for skill in skills:
                if any(keyword in skill.lower() for keyword in keywords):
                    found_skills.append(skill)
            
            if found_skills:
                categories[category] = {
                    'skills': found_skills,
                    'count': len(found_skills)
                }
        
        # 生成建议
        recommendations = self._generate_skill_recommendations(categories)
        
        return {
            'total_skills': len(skills),
            'categories': categories,
            'diversity_score': len(categories) * 10,  # 每个类别10分
            'recommendations': recommendations
        }
    
    def _analyze_experience(self, experience: List[Dict]) -> Dict:
        """工作经验分析"""
        if not experience:
            return {'total_positions': 0, 'years_experience': 0, 'level_assessment': 'entry'}
        
        total_positions = len(experience)
        years_experience = self._calculate_experience_years(experience)
        level_assessment = self._assess_experience_level(experience)
        
        # 分析职位进展
        career_progression = self._analyze_career_progression(experience)
        
        # 分析公司类型
        company_analysis = self._analyze_companies(experience)
        
        return {
            'total_positions': total_positions,
            'years_experience': years_experience,
            'level_assessment': level_assessment,
            'career_progression': career_progression,
            'company_analysis': company_analysis
        }
    
    def _analyze_education(self, education: List[Dict]) -> Dict:
        """教育背景分析"""
        if not education:
            return {'highest_degree': None, 'relevant_education': False}
        
        degrees = []
        relevant_fields = []
        
        for edu in education:
            degree = edu.get('degree', '').lower()
            field = edu.get('field', '').lower()
            
            if degree:
                degrees.append(degree)
            
            # 检查是否与技术相关
            if any(keyword in field for keyword in self.education_keywords['fields']):
                relevant_fields.append(field)
        
        highest_degree = self._determine_highest_degree(degrees)
        
        return {
            'total_degrees': len(education),
            'highest_degree': highest_degree,
            'relevant_education': len(relevant_fields) > 0,
            'relevant_fields': relevant_fields
        }
    
    def _analyze_content_quality(self, raw_text: str) -> Dict:
        """内容质量分析"""
        if not raw_text:
            return {'score': 0, 'issues': ['简历内容为空']}
        
        score = 0
        issues = []
        
        # 长度检查
        word_count = len(raw_text.split())
        if word_count < 100:
            issues.append('简历内容过短，建议增加更多详细信息')
        elif word_count > 1000:
            issues.append('简历内容过长，建议精简')
        else:
            score += 20
        
        # 结构检查
        if any(keyword in raw_text.lower() for keyword in ['experience', 'education', 'skills']):
            score += 20
        else:
            issues.append('缺少基本的简历结构')
        
        # 关键词检查
        if any(keyword in raw_text.lower() for keyword in ['project', 'achievement', 'responsible']):
            score += 15
        else:
            issues.append('缺少项目经验或成就描述')
        
        return {
            'score': score,
            'max_score': 55,
            'percentage': round((score / 55) * 100, 1),
            'word_count': word_count,
            'issues': issues
        }
    
    def _score_skills_section(self, skills: List[str]) -> Dict:
        """技能部分评分"""
        if not skills:
            return {'score': 0, 'max_score': 100, 'percentage': 0}
        
        score = 0
        
        # 技能数量评分
        skill_count = len(skills)
        if skill_count >= 15:
            score += 30
        elif skill_count >= 10:
            score += 25
        elif skill_count >= 5:
            score += 20
        else:
            score += 10
        
        # 技能多样性评分
        categories = 0
        for category, keywords in self.skill_categories.items():
            if any(keyword in ' '.join(skills).lower() for keyword in keywords):
                categories += 1
        
        score += categories * 10  # 每个类别10分
        
        return {
            'score': min(score, 100),
            'max_score': 100,
            'percentage': round(min(score, 100), 1)
        }
    
    def _score_experience_section(self, experience: List[Dict]) -> Dict:
        """经验部分评分"""
        if not experience:
            return {'score': 0, 'max_score': 100, 'percentage': 0}
        
        score = 0
        
        # 工作经验数量
        score += min(len(experience) * 15, 45)
        
        # 经验年限
        years = self._calculate_experience_years(experience)
        if years >= 5:
            score += 30
        elif years >= 3:
            score += 25
        elif years >= 1:
            score += 20
        else:
            score += 10
        
        # 职位层级
        level = self._assess_experience_level(experience)
        level_scores = {'entry': 10, 'junior': 15, 'mid': 20, 'senior': 25, 'executive': 30}
        score += level_scores.get(level, 10)
        
        return {
            'score': min(score, 100),
            'max_score': 100,
            'percentage': round(min(score, 100), 1)
        }
    
    def _score_education_section(self, education: List[Dict]) -> Dict:
        """教育部分评分"""
        if not education:
            return {'score': 20, 'max_score': 100, 'percentage': 20}  # 基础分
        
        score = 20  # 基础分
        
        # 学历层次
        degrees = [edu.get('degree', '').lower() for edu in education]
        if any('phd' in degree or '博士' in degree for degree in degrees):
            score += 40
        elif any('master' in degree or '硕士' in degree for degree in degrees):
            score += 30
        elif any('bachelor' in degree or '学士' in degree for degree in degrees):
            score += 20
        
        # 相关专业
        fields = [edu.get('field', '').lower() for edu in education]
        if any(keyword in ' '.join(fields) for keyword in self.education_keywords['fields']):
            score += 20
        
        return {
            'score': min(score, 100),
            'max_score': 100,
            'percentage': round(min(score, 100), 1)
        }
    
    def _calculate_overall_score(self, sections: Dict) -> float:
        """计算总体评分"""
        weights = {
            'basic_info': 0.15,
            'skills': 0.30,
            'experience': 0.35,
            'education': 0.15,
            'content_quality': 0.05
        }
        
        total_score = 0
        for section, weight in weights.items():
            if section in sections:
                score = sections[section].get('percentage', 0)
                total_score += score * weight
        
        return round(total_score, 1)
    
    def _generate_suggestions(self, analysis: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基本信息建议
        basic_info = analysis['sections'].get('basic_info', {})
        if basic_info.get('percentage', 0) < 80:
            suggestions.append("建议完善基本联系信息，包括姓名、邮箱和电话")
        
        # 技能建议
        skills = analysis.get('skills_analysis', {})
        if skills.get('total_skills', 0) < 10:
            suggestions.append("建议增加更多技能，特别是技术技能")
        
        skill_categories = skills.get('categories', {})
        if len(skill_categories) < 3:
            suggestions.append("建议增加技能多样性，涵盖更多技术领域")
        
        # 经验建议
        experience = analysis.get('experience_analysis', {})
        if experience.get('years_experience', 0) < 2:
            suggestions.append("建议补充项目经验或实习经历")
        
        # 教育建议
        education = analysis.get('education_analysis', {})
        if not education.get('relevant_education'):
            suggestions.append("如有相关技术教育背景，建议添加")
        
        # 内容质量建议
        content = analysis['sections'].get('content_quality', {})
        suggestions.extend(content.get('issues', []))
        
        return suggestions[:10]  # 限制建议数量
    
    def _identify_strengths(self, analysis: Dict) -> List[str]:
        """识别优势"""
        strengths = []
        
        # 检查各部分得分
        sections = analysis.get('sections', {})
        
        for section_name, section_data in sections.items():
            percentage = section_data.get('percentage', 0)
            if percentage >= 80:
                strength_map = {
                    'basic_info': '基本信息完整',
                    'skills': '技能丰富多样',
                    'experience': '工作经验丰富',
                    'education': '教育背景优秀',
                    'content_quality': '简历内容质量高'
                }
                strengths.append(strength_map.get(section_name, f'{section_name}表现优秀'))
        
        # 特殊优势识别
        skills = analysis.get('skills_analysis', {})
        if skills.get('total_skills', 0) >= 15:
            strengths.append('技能覆盖面广')
        
        experience = analysis.get('experience_analysis', {})
        if experience.get('years_experience', 0) >= 5:
            strengths.append('工作经验资深')
        
        return strengths
    
    def _identify_weaknesses(self, analysis: Dict) -> List[str]:
        """识别待改进项"""
        weaknesses = []
        
        sections = analysis.get('sections', {})
        
        for section_name, section_data in sections.items():
            percentage = section_data.get('percentage', 0)
            if percentage < 50:
                weakness_map = {
                    'basic_info': '基本信息不完整',
                    'skills': '技能展示不足',
                    'experience': '工作经验有限',
                    'education': '教育背景可以加强',
                    'content_quality': '简历内容需要改进'
                }
                weaknesses.append(weakness_map.get(section_name, f'{section_name}需要改进'))
        
        return weaknesses
    
    # 辅助方法
    def _is_valid_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _calculate_experience_years(self, experience: List[Dict]) -> float:
        """计算工作年限"""
        total_months = 0
        
        for exp in experience:
            duration = exp.get('duration', '')
            months = self._parse_duration_to_months(duration)
            total_months += months
        
        return round(total_months / 12, 1)
    
    def _parse_duration_to_months(self, duration: str) -> int:
        """解析时长为月数"""
        if not duration:
            return 12  # 默认1年
        
        duration = duration.lower()
        
        # 匹配各种格式
        year_match = re.search(r'(\d+)\s*(?:years?|年)', duration)
        month_match = re.search(r'(\d+)\s*(?:months?|个月|月)', duration)
        
        months = 0
        if year_match:
            months += int(year_match.group(1)) * 12
        if month_match:
            months += int(month_match.group(1))
        
        return max(months, 6)  # 最少6个月
    
    def _assess_experience_level(self, experience: List[Dict]) -> str:
        """评估经验级别"""
        positions = []
        for exp in experience:
            title = exp.get('title', '').lower()
            positions.append(title)
        
        all_titles = ' '.join(positions)
        
        # 检查级别关键词
        for level, keywords in self.experience_keywords.items():
            if any(keyword in all_titles for keyword in keywords):
                return level
        
        return 'mid'  # 默认中级
    
    def _analyze_career_progression(self, experience: List[Dict]) -> Dict:
        """分析职业发展路径"""
        if len(experience) < 2:
            return {'progression': 'insufficient_data'}
        
        # 简单的进步评估（基于职位标题）
        levels = []
        for exp in experience:
            title = exp.get('title', '').lower()
            level_score = 0
            
            if any(keyword in title for keyword in self.experience_keywords['executive']):
                level_score = 4
            elif any(keyword in title for keyword in self.experience_keywords['senior']):
                level_score = 3
            elif any(keyword in title for keyword in self.experience_keywords['mid']):
                level_score = 2
            elif any(keyword in title for keyword in self.experience_keywords['junior']):
                level_score = 1
            
            levels.append(level_score)
        
        if len(set(levels)) > 1 and max(levels) > min(levels):
            return {'progression': 'upward', 'levels': levels}
        else:
            return {'progression': 'stable', 'levels': levels}
    
    def _analyze_companies(self, experience: List[Dict]) -> Dict:
        """分析公司背景"""
        companies = [exp.get('company', '') for exp in experience]
        return {
            'total_companies': len(set(companies)),
            'companies': companies
        }
    
    def _determine_highest_degree(self, degrees: List[str]) -> Optional[str]:
        """确定最高学历"""
        degree_hierarchy = {
            'phd': 4, 'doctorate': 4, '博士': 4,
            'master': 3, '硕士': 3,
            'bachelor': 2, '学士': 2,
            'associate': 1, '专科': 1
        }
        
        max_level = 0
        highest = None
        
        for degree in degrees:
            for deg_name, level in degree_hierarchy.items():
                if deg_name in degree.lower():
                    if level > max_level:
                        max_level = level
                        highest = deg_name
        
        return highest
    
    def _generate_skill_recommendations(self, categories: Dict) -> List[str]:
        """生成技能建议"""
        recommendations = []
        
        # 检查缺失的技能类别
        missing_categories = []
        for category in self.skill_categories:
            if category not in categories:
                missing_categories.append(category)
        
        if 'programming_languages' in missing_categories:
            recommendations.append("建议添加编程语言技能")
        if 'frameworks' in missing_categories:
            recommendations.append("建议添加框架技能")
        if 'cloud_platforms' in missing_categories:
            recommendations.append("建议添加云平台技能")
        
        return recommendations[:5]  # 限制建议数量 