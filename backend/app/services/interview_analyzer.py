"""
Interview Analyzer Service
面试结果分析服务，提供答案质量评估、表现分析、智能评分等功能
"""

import re
import json
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import openai
from app.extensions import db
from app.models.question import Question, Answer, InterviewSession
import logging

logger = logging.getLogger(__name__)

class InterviewAnalyzer:
    """面试结果分析器"""
    
    def __init__(self):
        # 评分权重配置
        self.scoring_weights = {
            'answer_quality': 0.4,      # 答案质量40%
            'response_time': 0.2,       # 响应时间20%
            'completeness': 0.2,        # 完整性20%
            'technical_accuracy': 0.2   # 技术准确性20%
        }
        
        # 关键词库
        self.technical_keywords = {
            'programming': [
                'algorithm', 'data structure', 'complexity', 'optimization',
                'function', 'class', 'method', 'variable', 'loop', 'condition',
                'api', 'database', 'sql', 'framework', 'library', 'debugging'
            ],
            'experience': [
                'project', 'team', 'leadership', 'collaboration', 'management',
                'responsibility', 'achievement', 'challenge', 'solution', 'result'
            ],
            'soft_skills': [
                'communication', 'problem-solving', 'creativity', 'adaptability',
                'learning', 'initiative', 'teamwork', 'leadership', 'organization'
            ]
        }
        
        # 评分标准
        self.scoring_criteria = {
            'excellent': {'min': 90, 'description': '优秀'},
            'good': {'min': 75, 'description': '良好'},
            'average': {'min': 60, 'description': '一般'},
            'below_average': {'min': 45, 'description': '偏低'},
            'poor': {'min': 0, 'description': '较差'}
        }
    
    def analyze_interview_session(self, session_id: str, user_id: int) -> Dict:
        """
        分析整个面试会话
        
        Args:
            session_id: 面试会话ID
            user_id: 用户ID
            
        Returns:
            完整的面试分析结果
        """
        try:
            # 获取面试会话和答案
            session = InterviewSession.query.filter_by(
                session_id=session_id, 
                user_id=user_id
            ).first()
            
            if not session:
                raise ValueError(f"面试会话不存在: {session_id}")
            
            answers = Answer.query.filter_by(session_id=session.id).all()
            questions = Question.query.filter_by(session_id=session.id).all()
            
            # 执行各项分析
            analysis_result = {
                'session_info': self._get_session_info(session),
                'overall_score': 0,
                'section_scores': {},
                'answer_analysis': [],
                'performance_metrics': {},
                'strengths': [],
                'weaknesses': [],
                'recommendations': [],
                'detailed_feedback': {},
                'visualization_data': {},
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            # 答案质量分析
            analysis_result['answer_analysis'] = self._analyze_answers(answers, questions)
            
            # 计算各项得分
            analysis_result['section_scores'] = self._calculate_section_scores(
                answers, questions, analysis_result['answer_analysis']
            )
            
            # 计算总分
            analysis_result['overall_score'] = self._calculate_overall_score(
                analysis_result['section_scores']
            )
            
            # 性能指标分析
            analysis_result['performance_metrics'] = self._analyze_performance_metrics(
                answers, questions, session
            )
            
            # 优势和劣势分析
            analysis_result['strengths'], analysis_result['weaknesses'] = \
                self._identify_strengths_and_weaknesses(analysis_result)
            
            # 生成改进建议
            analysis_result['recommendations'] = self._generate_recommendations(
                analysis_result
            )
            
            # 详细反馈
            analysis_result['detailed_feedback'] = self._generate_detailed_feedback(
                analysis_result
            )
            
            # 可视化数据
            analysis_result['visualization_data'] = self._prepare_visualization_data(
                analysis_result
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"面试分析失败: {str(e)}")
            return {
                'error': str(e),
                'session_id': session_id,
                'analysis_date': datetime.utcnow().isoformat()
            }
    
    def _get_session_info(self, session: InterviewSession) -> Dict:
        """获取会话基本信息"""
        return {
            'session_id': session.session_id,
            'interview_type': self._get_enum_value(session.interview_type),
            'title': session.title,
            'total_questions': session.total_questions,
            'completed_questions': session.completed_questions,
            'start_time': session.started_at.isoformat() if session.started_at else None,
            'end_time': session.completed_at.isoformat() if session.completed_at else None,
            'duration_minutes': self._calculate_duration(session),
            'status': session.status
        }
    
    def _get_enum_value(self, enum_obj):
        """安全获取枚举值"""
        if enum_obj is None:
            return None
        if hasattr(enum_obj, 'value'):
            return enum_obj.value
        return str(enum_obj)
    
    def _analyze_answers(self, answers: List[Answer], questions: List[Question]) -> List[Dict]:
        """分析所有答案"""
        analysis_results = []
        
        for answer in answers:
            question = next((q for q in questions if q.id == answer.question_id), None)
            if question:
                answer_analysis = self._analyze_single_answer(answer, question)
                analysis_results.append(answer_analysis)
        
        return analysis_results
    
    def _analyze_single_answer(self, answer: Answer, question: Question) -> Dict:
        """分析单个答案"""
        analysis = {
            'question_id': question.id,
            'question_type': self._get_enum_value(question.question_type),
            'question_difficulty': self._get_enum_value(question.difficulty),
            'question_text': question.question_text[:100] + "...",
            'answer_text': answer.answer_text or "",
            'response_time_seconds': answer.response_time or 0,
            'answered_at': answer.answered_at.isoformat() if answer.answered_at else None
        }
        
        # 答案质量评分
        analysis['quality_score'] = self._score_answer_quality(
            answer.answer_text, question
        )
        
        # 响应时间评分
        difficulty_value = self._get_enum_value(question.difficulty)
        analysis['time_score'] = self._score_response_time(
            answer.response_time, difficulty_value
        )
        
        # 完整性评分
        analysis['completeness_score'] = self._score_completeness(
            answer.answer_text, question
        )
        
        # 技术准确性评分
        analysis['technical_score'] = self._score_technical_accuracy(
            answer.answer_text, question
        )
        
        # 综合得分
        analysis['total_score'] = self._calculate_answer_total_score(analysis)
        
        # 关键词分析
        analysis['keywords_found'] = self._extract_keywords(answer.answer_text)
        
        # 答案长度分析
        analysis['answer_length'] = len(answer.answer_text or "")
        analysis['word_count'] = len((answer.answer_text or "").split())
        
        return analysis
    
    def _score_answer_quality(self, answer_text: str, question: Question) -> float:
        """评分答案质量"""
        if not answer_text:
            return 0.0
        
        score = 0.0
        
        # 基础长度检查
        word_count = len(answer_text.split())
        if word_count >= 50:
            score += 30
        elif word_count >= 20:
            score += 20
        elif word_count >= 10:
            score += 10
        
        # 结构化检查
        if any(marker in answer_text.lower() for marker in ['first', 'second', 'finally', '1.', '2.', '3.']):
            score += 15
        
        # 技术词汇检查
        technical_words = 0
        for category, keywords in self.technical_keywords.items():
            for keyword in keywords:
                if keyword.lower() in answer_text.lower():
                    technical_words += 1
        
        if technical_words >= 5:
            score += 25
        elif technical_words >= 3:
            score += 15
        elif technical_words >= 1:
            score += 10
        
        # 实例和具体化检查
        if any(indicator in answer_text.lower() for indicator in ['example', 'for instance', 'such as', '例如']):
            score += 15
        
        # 问题相关性检查
        question_keywords = self._extract_question_keywords(question.question_text)
        relevance_score = self._calculate_relevance(answer_text, question_keywords)
        score += relevance_score * 15
        
        return min(score, 100.0)
    
    def _score_response_time(self, response_time: Optional[int], difficulty: str) -> float:
        """评分响应时间"""
        if not response_time:
            return 50.0  # 默认中等分数
        
        # 根据难度设置期望时间（秒）
        expected_times = {
            'easy': 120,    # 2分钟
            'medium': 300,  # 5分钟
            'hard': 600     # 10分钟
        }
        
        expected_time = expected_times.get(difficulty, 300)
        
        # 计算时间效率分数
        if response_time <= expected_time * 0.5:
            return 100.0  # 非常快
        elif response_time <= expected_time:
            return 85.0   # 正常速度
        elif response_time <= expected_time * 1.5:
            return 70.0   # 稍慢
        elif response_time <= expected_time * 2:
            return 50.0   # 较慢
        else:
            return 30.0   # 很慢
    
    def _score_completeness(self, answer_text: str, question: Question) -> float:
        """评分答案完整性"""
        if not answer_text:
            return 0.0
        
        score = 0.0
        
        # 基础完整性
        word_count = len(answer_text.split())
        if word_count >= 100:
            score += 40
        elif word_count >= 50:
            score += 30
        elif word_count >= 20:
            score += 20
        elif word_count >= 10:
            score += 10
        
        # 问题类型特定的完整性检查
        question_type = self._get_enum_value(question.question_type)
        
        if question_type == 'behavioral':
            # STAR方法检查 (Situation, Task, Action, Result)
            star_indicators = ['situation', 'task', 'action', 'result', 'challenge', 'outcome']
            found_indicators = sum(1 for indicator in star_indicators 
                                 if indicator in answer_text.lower())
            score += min(found_indicators * 10, 30)
        
        elif question_type == 'technical':
            # 技术问题完整性检查
            tech_indicators = ['algorithm', 'complexity', 'implementation', 'solution', 'approach']
            found_indicators = sum(1 for indicator in tech_indicators 
                                 if indicator in answer_text.lower())
            score += min(found_indicators * 8, 30)
        
        # 结论和总结检查
        conclusion_indicators = ['conclusion', 'summary', 'in summary', 'overall', 'finally']
        if any(indicator in answer_text.lower() for indicator in conclusion_indicators):
            score += 15
        
        return min(score, 100.0)
    
    def _score_technical_accuracy(self, answer_text: str, question: Question) -> float:
        """评分技术准确性"""
        if not answer_text:
            return 0.0
        
        score = 50.0  # 基础分
        
        # 技术词汇准确性
        technical_terms = 0
        for category, keywords in self.technical_keywords.items():
            for keyword in keywords:
                if keyword.lower() in answer_text.lower():
                    technical_terms += 1
        
        # 技术术语使用得分
        if technical_terms >= 8:
            score += 30
        elif technical_terms >= 5:
            score += 20
        elif technical_terms >= 3:
            score += 15
        elif technical_terms >= 1:
            score += 10
        
        # 避免常见错误
        common_errors = ['definitely', 'always works', 'never fails', 'impossible']
        error_count = sum(1 for error in common_errors if error in answer_text.lower())
        score -= error_count * 5
        
        # 准确性指标
        accuracy_indicators = ['specifically', 'precisely', 'according to', 'research shows']
        accuracy_count = sum(1 for indicator in accuracy_indicators 
                           if indicator in answer_text.lower())
        score += accuracy_count * 5
        
        return max(min(score, 100.0), 0.0)
    
    def _calculate_answer_total_score(self, analysis: Dict) -> float:
        """计算单个答案的总分"""
        return (
            analysis['quality_score'] * self.scoring_weights['answer_quality'] +
            analysis['time_score'] * self.scoring_weights['response_time'] +
            analysis['completeness_score'] * self.scoring_weights['completeness'] +
            analysis['technical_score'] * self.scoring_weights['technical_accuracy']
        )
    
    def _calculate_section_scores(self, answers: List[Answer], questions: List[Question], 
                                answer_analysis: List[Dict]) -> Dict:
        """计算各部分得分"""
        if not answer_analysis:
            return {}
        
        # 按问题类型分组
        type_scores = {}
        type_counts = {}
        
        for analysis in answer_analysis:
            question_type = analysis['question_type']
            score = analysis['total_score']
            
            if question_type not in type_scores:
                type_scores[question_type] = []
            
            type_scores[question_type].append(score)
        
        # 计算平均分
        section_scores = {}
        for question_type, scores in type_scores.items():
            section_scores[question_type] = {
                'average_score': statistics.mean(scores),
                'count': len(scores),
                'max_score': max(scores),
                'min_score': min(scores)
            }
        
        return section_scores
    
    def _calculate_overall_score(self, section_scores: Dict) -> float:
        """计算总体得分"""
        if not section_scores:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        # 权重配置
        type_weights = {
            'technical': 0.4,
            'behavioral': 0.3,
            'situational': 0.2,
            'cultural_fit': 0.1
        }
        
        for question_type, scores in section_scores.items():
            weight = type_weights.get(question_type, 0.25)
            total_score += scores['average_score'] * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _analyze_performance_metrics(self, answers: List[Answer], questions: List[Question], 
                                   session: InterviewSession) -> Dict:
        """分析性能指标"""
        metrics = {
            'total_questions': len(questions),
            'answered_questions': len([a for a in answers if a.answer_text]),
            'completion_rate': 0.0,
            'average_response_time': 0.0,
            'total_session_time': 0.0,
            'response_time_distribution': {},
            'question_type_distribution': {}
        }
        
        # 完成率
        if metrics['total_questions'] > 0:
            metrics['completion_rate'] = metrics['answered_questions'] / metrics['total_questions']
        
        # 响应时间分析
        response_times = [a.response_time for a in answers if a.response_time]
        if response_times:
            metrics['average_response_time'] = statistics.mean(response_times)
            metrics['response_time_distribution'] = {
                'min': min(response_times),
                'max': max(response_times),
                'median': statistics.median(response_times),
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
        
        # 会话总时长
        if session.started_at and session.completed_at:
            duration = session.completed_at - session.started_at
            metrics['total_session_time'] = duration.total_seconds()
        
        # 问题类型分布
        type_counts = Counter(self._get_enum_value(q.question_type) for q in questions)
        metrics['question_type_distribution'] = dict(type_counts)
        
        return metrics
    
    def _identify_strengths_and_weaknesses(self, analysis: Dict) -> Tuple[List[str], List[str]]:
        """识别优势和劣势"""
        strengths = []
        weaknesses = []
        
        overall_score = analysis['overall_score']
        section_scores = analysis['section_scores']
        performance_metrics = analysis['performance_metrics']
        
        # 基于总分的评估
        if overall_score >= 85:
            strengths.append("整体表现优秀，回答质量高")
        elif overall_score >= 70:
            strengths.append("整体表现良好")
        else:
            weaknesses.append("整体表现有待提升")
        
        # 基于完成率的评估
        completion_rate = performance_metrics.get('completion_rate', 0)
        if completion_rate >= 0.9:
            strengths.append("问题完成率高，坚持完成面试")
        elif completion_rate < 0.7:
            weaknesses.append("问题完成率偏低，建议合理安排时间")
        
        # 基于响应时间的评估
        avg_response_time = performance_metrics.get('average_response_time', 0)
        if avg_response_time > 0:
            if avg_response_time <= 180:  # 3分钟以内
                strengths.append("思考敏捷，回答速度适中")
            elif avg_response_time >= 600:  # 10分钟以上
                weaknesses.append("思考时间较长，可能需要提高反应速度")
        
        # 基于各类型分数的评估
        for question_type, scores in section_scores.items():
            avg_score = scores['average_score']
            if avg_score >= 80:
                strengths.append(f"{question_type}类问题表现突出")
            elif avg_score < 60:
                weaknesses.append(f"{question_type}类问题需要加强")
        
        return strengths, weaknesses
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        overall_score = analysis['overall_score']
        section_scores = analysis['section_scores']
        weaknesses = analysis['weaknesses']
        
        # 基于总分的建议
        if overall_score < 70:
            recommendations.append("建议多练习面试问题，提高回答的结构化和逻辑性")
        
        # 基于各部分分数的建议
        for question_type, scores in section_scores.items():
            avg_score = scores['average_score']
            if avg_score < 60:
                if question_type == 'technical':
                    recommendations.append("加强技术基础知识学习，多做技术实践项目")
                elif question_type == 'behavioral':
                    recommendations.append("准备更多具体的工作经历实例，使用STAR方法组织回答")
                elif question_type == 'situational':
                    recommendations.append("多思考实际工作场景，提高问题分析和解决能力")
        
        # 基于答案分析的建议
        answer_analysis = analysis.get('answer_analysis', [])
        if answer_analysis:
            avg_word_count = statistics.mean([a.get('word_count', 0) for a in answer_analysis])
            if avg_word_count < 30:
                recommendations.append("回答可以更详细，提供更多具体细节和例子")
        
        # 通用建议
        if len(recommendations) == 0:
            recommendations.append("继续保持良好表现，可以在技术深度和沟通表达上进一步提升")
        
        return recommendations[:10]  # 限制建议数量
    
    def _generate_detailed_feedback(self, analysis: Dict) -> Dict:
        """生成详细反馈"""
        feedback = {
            'overall_assessment': self._get_overall_assessment(analysis['overall_score']),
            'section_feedback': {},
            'improvement_areas': [],
            'next_steps': []
        }
        
        # 各部分详细反馈
        for question_type, scores in analysis['section_scores'].items():
            avg_score = scores['average_score']
            feedback['section_feedback'][question_type] = {
                'score': avg_score,
                'level': self._get_score_level(avg_score),
                'feedback': self._get_section_feedback(question_type, avg_score)
            }
        
        # 改进重点
        feedback['improvement_areas'] = self._identify_improvement_areas(analysis)
        
        # 下一步建议
        feedback['next_steps'] = self._suggest_next_steps(analysis)
        
        return feedback
    
    def _prepare_visualization_data(self, analysis: Dict) -> Dict:
        """准备可视化数据"""
        viz_data = {
            'score_radar': {},
            'response_time_chart': {},
            'completion_progress': {},
            'score_distribution': {},
            'performance_trend': {}
        }
        
        # 雷达图数据（各维度分数）
        section_scores = analysis['section_scores']
        viz_data['score_radar'] = {
            'categories': list(section_scores.keys()),
            'scores': [scores['average_score'] for scores in section_scores.values()]
        }
        
        # 响应时间图表
        answer_analysis = analysis.get('answer_analysis', [])
        if answer_analysis:
            viz_data['response_time_chart'] = {
                'questions': [f"Q{i+1}" for i in range(len(answer_analysis))],
                'times': [a.get('response_time_seconds', 0) for a in answer_analysis]
            }
        
        # 完成进度
        performance_metrics = analysis['performance_metrics']
        viz_data['completion_progress'] = {
            'completed': performance_metrics.get('answered_questions', 0),
            'total': performance_metrics.get('total_questions', 0),
            'percentage': performance_metrics.get('completion_rate', 0) * 100
        }
        
        # 分数分布
        if answer_analysis:
            scores = [a.get('total_score', 0) for a in answer_analysis]
            viz_data['score_distribution'] = {
                'excellent': len([s for s in scores if s >= 90]),
                'good': len([s for s in scores if 75 <= s < 90]),
                'average': len([s for s in scores if 60 <= s < 75]),
                'below_average': len([s for s in scores if s < 60])
            }
        
        return viz_data
    
    # 辅助方法
    def _calculate_duration(self, session: InterviewSession) -> Optional[float]:
        """计算面试时长（分钟）"""
        if session.started_at and session.completed_at:
            duration = session.completed_at - session.started_at
            return duration.total_seconds() / 60
        return None
    
    def _extract_keywords(self, text: str) -> Dict:
        """提取关键词"""
        if not text:
            return {}
        
        found_keywords = {}
        for category, keywords in self.technical_keywords.items():
            found_keywords[category] = []
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    found_keywords[category].append(keyword)
        
        return found_keywords
    
    def _extract_question_keywords(self, question_text: str) -> List[str]:
        """从问题中提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'\b\w+\b', question_text.lower())
        # 过滤停用词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [word for word in words if len(word) > 3 and word not in stop_words]
    
    def _calculate_relevance(self, answer_text: str, question_keywords: List[str]) -> float:
        """计算答案与问题的相关性"""
        if not answer_text or not question_keywords:
            return 0.0
        
        answer_words = set(re.findall(r'\b\w+\b', answer_text.lower()))
        question_words = set(question_keywords)
        
        intersection = answer_words.intersection(question_words)
        union = answer_words.union(question_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _get_overall_assessment(self, score: float) -> str:
        """获取总体评价"""
        for level, criteria in self.scoring_criteria.items():
            if score >= criteria['min']:
                return criteria['description']
        return '需要改进'
    
    def _get_score_level(self, score: float) -> str:
        """获取分数等级"""
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'average'
        else:
            return 'below_average'
    
    def _get_section_feedback(self, question_type: str, score: float) -> str:
        """获取部分反馈"""
        level = self._get_score_level(score)
        
        feedback_templates = {
            'technical': {
                'excellent': '技术问题回答优秀，展现了深厚的技术功底',
                'good': '技术回答良好，基础扎实，可在深度上进一步提升',
                'average': '技术回答一般，建议加强基础知识学习',
                'below_average': '技术回答需要改进，建议系统学习相关技术'
            },
            'behavioral': {
                'excellent': '行为问题回答优秀，很好地展示了经验和能力',
                'good': '行为回答良好，经验描述较为清晰',
                'average': '行为回答一般，可以提供更多具体实例',
                'below_average': '行为回答需要改进，建议使用STAR方法组织回答'
            }
        }
        
        return feedback_templates.get(question_type, {}).get(level, '需要进一步提升')
    
    def _identify_improvement_areas(self, analysis: Dict) -> List[str]:
        """识别改进重点"""
        areas = []
        
        # 基于弱项识别
        section_scores = analysis['section_scores']
        for question_type, scores in section_scores.items():
            if scores['average_score'] < 70:
                areas.append(f"{question_type}类问题回答技巧")
        
        # 基于答案分析识别
        answer_analysis = analysis.get('answer_analysis', [])
        if answer_analysis:
            avg_quality = statistics.mean([a.get('quality_score', 0) for a in answer_analysis])
            avg_completeness = statistics.mean([a.get('completeness_score', 0) for a in answer_analysis])
            
            if avg_quality < 70:
                areas.append("回答质量和逻辑性")
            if avg_completeness < 70:
                areas.append("回答完整性和结构化")
        
        return areas[:5]  # 限制数量
    
    def _suggest_next_steps(self, analysis: Dict) -> List[str]:
        """建议下一步行动"""
        steps = []
        
        overall_score = analysis['overall_score']
        
        if overall_score < 60:
            steps.append("系统复习面试基础知识和技巧")
            steps.append("准备更多具体的工作实例")
        elif overall_score < 75:
            steps.append("针对薄弱环节进行专项练习")
            steps.append("参加模拟面试提高实战经验")
        else:
            steps.append("保持良好状态，可挑战更高难度的面试")
            steps.append("分享经验帮助他人提升面试技能")
        
        steps.append("定期回顾面试反馈，持续改进")
        
        return steps[:5] 