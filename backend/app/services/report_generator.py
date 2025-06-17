"""
Report Generator Service
面试报告生成器，生成专业的面试分析报告
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from app.services.interview_analyzer import InterviewAnalyzer
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """面试报告生成器"""
    
    def __init__(self):
        self.analyzer = InterviewAnalyzer()
        
        # 报告模板配置
        self.report_templates = {
            'comprehensive': {
                'name': '综合分析报告',
                'sections': [
                    'executive_summary', 'session_overview', 'performance_analysis',
                    'section_breakdown', 'strengths_weaknesses', 'recommendations',
                    'detailed_feedback', 'improvement_plan', 'appendix'
                ]
            },
            'summary': {
                'name': '摘要报告',
                'sections': [
                    'executive_summary', 'key_metrics', 'top_recommendations'
                ]
            },
            'technical': {
                'name': '技术评估报告',
                'sections': [
                    'technical_overview', 'skill_assessment', 'code_quality',
                    'problem_solving', 'technical_recommendations'
                ]
            }
        }
    
    def generate_comprehensive_report(self, session_id: str, user_id: int) -> Dict:
        """
        生成综合分析报告
        
        Args:
            session_id: 面试会话ID
            user_id: 用户ID
            
        Returns:
            完整的综合分析报告
        """
        try:
            # 获取分析结果
            analysis_result = self.analyzer.analyze_interview_session(session_id, user_id)
            
            if 'error' in analysis_result:
                return {'error': f"分析失败: {analysis_result['error']}"}
            
            # 生成综合报告
            report = {
                'report_metadata': {
                    'report_id': f"comprehensive_{session_id}_{int(datetime.utcnow().timestamp())}",
                    'type': 'comprehensive',
                    'generated_at': datetime.utcnow().isoformat(),
                    'version': '1.0',
                    'session_id': session_id
                },
                'executive_summary': self._generate_executive_summary(analysis_result),
                'session_overview': self._generate_session_overview(analysis_result),
                'performance_analysis': self._generate_performance_analysis(analysis_result),
                'section_breakdown': self._generate_section_breakdown(analysis_result),
                'strengths_weaknesses': self._generate_strengths_weaknesses(analysis_result),
                'recommendations': self._generate_recommendations_section(analysis_result),
                'detailed_feedback': self._generate_detailed_feedback_section(analysis_result),
                'improvement_plan': self._generate_improvement_plan(analysis_result),
                'appendix': self._generate_appendix(analysis_result)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"综合报告生成失败: {str(e)}")
            return {'error': f"报告生成失败: {str(e)}"}
    
    def generate_summary_report(self, session_id: str, user_id: int) -> Dict:
        """生成摘要报告"""
        try:
            analysis_result = self.analyzer.analyze_interview_session(session_id, user_id)
            
            if 'error' in analysis_result:
                return {'error': f"分析失败: {analysis_result['error']}"}
            
            report = {
                'report_metadata': {
                    'report_id': f"summary_{session_id}_{int(datetime.utcnow().timestamp())}",
                    'type': 'summary',
                    'generated_at': datetime.utcnow().isoformat(),
                    'session_id': session_id
                },
                'executive_summary': self._generate_executive_summary(analysis_result),
                'key_metrics': self._generate_key_metrics(analysis_result),
                'top_recommendations': self._get_top_recommendations(analysis_result)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"摘要报告生成失败: {str(e)}")
            return {'error': f"报告生成失败: {str(e)}"}
    
    def generate_technical_report(self, session_id: str, user_id: int) -> Dict:
        """生成技术评估报告"""
        try:
            analysis_result = self.analyzer.analyze_interview_session(session_id, user_id)
            
            if 'error' in analysis_result:
                return {'error': f"分析失败: {analysis_result['error']}"}
            
            report = {
                'report_metadata': {
                    'report_id': f"technical_{session_id}_{int(datetime.utcnow().timestamp())}",
                    'type': 'technical',
                    'generated_at': datetime.utcnow().isoformat(),
                    'session_id': session_id
                },
                'technical_overview': self._generate_technical_overview(analysis_result),
                'skill_assessment': self._generate_skill_assessment(analysis_result),
                'problem_solving': self._generate_problem_solving_analysis(analysis_result),
                'technical_recommendations': self._generate_technical_recommendations(analysis_result)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"技术报告生成失败: {str(e)}")
            return {'error': f"报告生成失败: {str(e)}"}
    
    def _generate_executive_summary(self, analysis_result: Dict) -> Dict:
        """生成执行摘要"""
        overall_score = analysis_result['overall_score']
        session_info = analysis_result['session_info']
        performance_metrics = analysis_result['performance_metrics']
        
        # 确定总体评价
        if overall_score >= 90:
            performance_level = "优秀"
            recommendation = "表现卓越，建议进入下一轮面试"
        elif overall_score >= 75:
            performance_level = "良好"
            recommendation = "表现良好，可考虑进入下一轮"
        elif overall_score >= 60:
            performance_level = "一般"
            recommendation = "表现一般，需要进一步评估"
        else:
            performance_level = "待改进"
            recommendation = "需要额外培训和改进"
        
        return {
            'overall_assessment': {
                'score': round(overall_score, 1),
                'grade': self._get_letter_grade(overall_score),
                'performance_level': performance_level,
                'recommendation': recommendation
            },
            'key_highlights': [
                f"面试类型: {session_info['interview_type']}",
                f"完成率: {performance_metrics['completion_rate']:.1%}",
                f"平均响应时间: {performance_metrics.get('average_response_time', 0):.0f}秒",
                f"总面试时长: {session_info.get('duration_minutes', 0):.0f}分钟"
            ],
            'top_strengths': analysis_result['strengths'][:3],
            'primary_concerns': analysis_result['weaknesses'][:2],
            'immediate_next_steps': analysis_result['recommendations'][:2]
        }
    
    def _generate_session_overview(self, analysis_result: Dict) -> Dict:
        """生成会话概览"""
        session_info = analysis_result['session_info']
        performance_metrics = analysis_result['performance_metrics']
        
        return {
            'basic_information': {
                'session_id': session_info['session_id'],
                'title': session_info['title'],
                'interview_type': session_info['interview_type'],
                'date': session_info['start_time'][:10] if session_info['start_time'] else 'N/A',
                'duration': f"{session_info.get('duration_minutes', 0):.0f} 分钟"
            },
            'participation_metrics': {
                'total_questions': performance_metrics['total_questions'],
                'answered_questions': performance_metrics['answered_questions'],
                'completion_rate': f"{performance_metrics['completion_rate']:.1%}",
                'average_response_time': f"{performance_metrics.get('average_response_time', 0):.0f} 秒"
            },
            'question_distribution': performance_metrics.get('question_type_distribution', {}),
            'session_timeline': self._create_session_timeline(analysis_result)
        }
    
    def _generate_performance_analysis(self, analysis_result: Dict) -> Dict:
        """生成表现分析"""
        section_scores = analysis_result['section_scores']
        answer_analysis = analysis_result.get('answer_analysis', [])
        
        # 计算各维度平均分
        dimension_scores = {
            'answer_quality': 0,
            'response_time': 0,
            'completeness': 0,
            'technical_accuracy': 0
        }
        
        if answer_analysis:
            for dimension in dimension_scores:
                scores = [a.get(f"{dimension.split('_')[0]}_score", 0) for a in answer_analysis]
                dimension_scores[dimension] = sum(scores) / len(scores) if scores else 0
        
        return {
            'overall_metrics': {
                'total_score': round(analysis_result['overall_score'], 1),
                'percentile_rank': self._calculate_percentile_rank(analysis_result['overall_score']),
                'performance_consistency': self._calculate_consistency(answer_analysis)
            },
            'dimension_analysis': {
                dimension: {
                    'score': round(score, 1),
                    'grade': self._get_letter_grade(score),
                    'interpretation': self._interpret_dimension_score(dimension, score)
                }
                for dimension, score in dimension_scores.items()
            },
            'section_performance': {
                section: {
                    'average_score': round(scores['average_score'], 1),
                    'question_count': scores['count'],
                    'score_range': f"{round(scores['min_score'], 1)} - {round(scores['max_score'], 1)}",
                    'consistency': self._calculate_section_consistency(scores)
                }
                for section, scores in section_scores.items()
            },
            'performance_trends': self._analyze_performance_trends(answer_analysis)
        }
    
    def _generate_section_breakdown(self, analysis_result: Dict) -> Dict:
        """生成分段分析"""
        section_scores = analysis_result['section_scores']
        answer_analysis = analysis_result.get('answer_analysis', [])
        
        breakdown = {}
        
        for section, scores in section_scores.items():
            # 获取该类型的所有答案分析
            section_answers = [a for a in answer_analysis if a.get('question_type') == section]
            
            breakdown[section] = {
                'overview': {
                    'question_count': scores['count'],
                    'average_score': round(scores['average_score'], 1),
                    'best_performance': round(scores['max_score'], 1),
                    'weakest_performance': round(scores['min_score'], 1),
                    'grade': self._get_letter_grade(scores['average_score'])
                },
                'detailed_analysis': {
                    'strengths': self._identify_section_strengths(section, section_answers),
                    'weaknesses': self._identify_section_weaknesses(section, section_answers),
                    'improvement_suggestions': self._generate_section_improvements(section, scores['average_score']),
                    'standout_responses': self._identify_standout_responses(section_answers)
                },
                'question_breakdown': [
                    {
                        'question_id': answer.get('question_id'),
                        'difficulty': answer.get('question_difficulty'),
                        'score': round(answer.get('total_score', 0), 1),
                        'response_time': f"{answer.get('response_time_seconds', 0)} 秒",
                        'key_insights': self._generate_question_insights(answer)
                    }
                    for answer in section_answers
                ]
            }
        
        return breakdown
    
    def _generate_strengths_weaknesses(self, analysis_result: Dict) -> Dict:
        """生成优势劣势分析"""
        return {
            'strengths': {
                'identified_strengths': analysis_result['strengths'],
                'evidence': self._find_strength_evidence(analysis_result),
                'leverage_opportunities': self._suggest_strength_leverage(analysis_result['strengths'])
            },
            'weaknesses': {
                'identified_weaknesses': analysis_result['weaknesses'],
                'impact_assessment': self._assess_weakness_impact(analysis_result['weaknesses']),
                'improvement_priorities': self._prioritize_improvements(analysis_result['weaknesses'])
            },
            'gap_analysis': self._perform_gap_analysis(analysis_result),
            'development_roadmap': self._create_development_roadmap(analysis_result)
        }
    
    def _generate_recommendations_section(self, analysis_result: Dict) -> Dict:
        """生成建议部分"""
        recommendations = analysis_result['recommendations']
        
        return {
            'immediate_actions': recommendations[:3],
            'short_term_goals': self._generate_short_term_goals(analysis_result),
            'long_term_development': self._generate_long_term_development(analysis_result),
            'resource_suggestions': self._suggest_resources(analysis_result),
            'practice_plan': self._create_practice_plan(analysis_result)
        }
    
    def _generate_detailed_feedback_section(self, analysis_result: Dict) -> Dict:
        """生成详细反馈部分"""
        detailed_feedback = analysis_result['detailed_feedback']
        
        return {
            'section_feedback': detailed_feedback.get('section_feedback', {}),
            'improvement_areas': detailed_feedback.get('improvement_areas', []),
            'specific_observations': self._generate_specific_observations(analysis_result),
            'behavioral_insights': self._generate_behavioral_insights(analysis_result),
            'communication_assessment': self._assess_communication_style(analysis_result)
        }
    
    def _generate_improvement_plan(self, analysis_result: Dict) -> Dict:
        """生成改进计划"""
        overall_score = analysis_result['overall_score']
        weaknesses = analysis_result['weaknesses']
        
        # 基于分数确定改进紧急程度
        if overall_score < 60:
            urgency = "高"
            timeline = "1-2个月"
        elif overall_score < 75:
            urgency = "中"
            timeline = "2-3个月"
        else:
            urgency = "低"
            timeline = "3-6个月"
        
        return {
            'improvement_priorities': {
                'urgency_level': urgency,
                'recommended_timeline': timeline,
                'focus_areas': weaknesses[:3]
            },
            'action_items': self._create_action_items(analysis_result),
            'milestone_schedule': self._create_milestone_schedule(analysis_result),
            'success_metrics': self._define_success_metrics(analysis_result),
            'follow_up_plan': self._create_follow_up_plan(analysis_result)
        }
    
    def _generate_appendix(self, analysis_result: Dict) -> Dict:
        """生成附录"""
        return {
            'scoring_methodology': {
                'overall_calculation': "综合各维度加权平均",
                'dimension_weights': {
                    'answer_quality': '40%',
                    'response_time': '20%',
                    'completeness': '20%',
                    'technical_accuracy': '20%'
                },
                'grading_scale': {
                    'A+': '90-100分',
                    'A': '85-89分',
                    'A-': '80-84分',
                    'B+': '75-79分',
                    'B': '70-74分',
                    'C+': '60-69分',
                    'C': '50-59分',
                    'D': '0-49分'
                }
            },
            'raw_data': {
                'answer_analysis': analysis_result.get('answer_analysis', []),
                'performance_metrics': analysis_result['performance_metrics'],
                'visualization_data': analysis_result.get('visualization_data', {})
            },
            'technical_details': {
                'analysis_algorithm': "基于NLP和统计分析的多维度评估",
                'confidence_level': "85%",
                'analysis_date': analysis_result['analysis_date']
            }
        }
    
    # 辅助方法
    def _get_letter_grade(self, score: float) -> str:
        """获取字母等级"""
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'A-'
        elif score >= 75: return 'B+'
        elif score >= 70: return 'B'
        elif score >= 65: return 'B-'
        elif score >= 60: return 'C+'
        elif score >= 55: return 'C'
        else: return 'D'
    
    def _calculate_percentile_rank(self, score: float) -> int:
        """计算百分位排名"""
        if score >= 90: return 95
        elif score >= 80: return 85
        elif score >= 70: return 70
        elif score >= 60: return 50
        else: return 25
    
    def _calculate_consistency(self, answer_analysis: List[Dict]) -> float:
        """计算表现一致性"""
        if len(answer_analysis) < 2:
            return 100.0
        
        scores = [a.get('total_score', 0) for a in answer_analysis]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # 一致性 = 100 - (标准差 / 平均分 * 100)
        consistency = max(0, 100 - (std_dev / mean_score * 100)) if mean_score > 0 else 0
        return round(consistency, 1)
    
    def _interpret_dimension_score(self, dimension: str, score: float) -> str:
        """解释维度分数"""
        interpretations = {
            'answer_quality': {
                'high': '回答质量优秀，逻辑清晰，内容丰富',
                'medium': '回答质量良好，有一定深度',
                'low': '回答质量需要提升，建议加强逻辑性'
            },
            'response_time': {
                'high': '响应迅速，思维敏捷',
                'medium': '响应时间适中',
                'low': '思考时间较长，可能需要提高反应速度'
            },
            'completeness': {
                'high': '回答完整详细，覆盖了问题的各个方面',
                'medium': '回答相对完整',
                'low': '回答不够完整，建议增加细节和例子'
            },
            'technical_accuracy': {
                'high': '技术表达准确，使用专业术语恰当',
                'medium': '技术理解基本正确',
                'low': '技术理解有待加强，建议深入学习'
            }
        }
        
        level = 'high' if score >= 75 else 'medium' if score >= 60 else 'low'
        return interpretations.get(dimension, {}).get(level, '需要进一步评估')
    
    def _calculate_section_consistency(self, scores: Dict) -> str:
        """计算部分一致性"""
        score_range = scores['max_score'] - scores['min_score']
        if score_range <= 10:
            return "非常稳定"
        elif score_range <= 20:
            return "相对稳定"
        elif score_range <= 30:
            return "有波动"
        else:
            return "波动较大"
    
    def _analyze_performance_trends(self, answer_analysis: List[Dict]) -> Dict:
        """分析表现趋势"""
        if len(answer_analysis) < 3:
            return {'trend': '数据不足', 'pattern': '无法判断'}
        
        scores = [a.get('total_score', 0) for a in answer_analysis]
        
        # 简单线性趋势分析
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = sum(scores) / n
        
        slope_numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
        slope_denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if slope_denominator == 0:
            trend = '稳定'
        else:
            slope = slope_numerator / slope_denominator
            if slope > 2:
                trend = '持续改善'
            elif slope > 0.5:
                trend = '轻微改善'
            elif slope < -2:
                trend = '表现下降'
            elif slope < -0.5:
                trend = '轻微下降'
            else:
                trend = '相对稳定'
        
        return {
            'trend': trend,
            'slope': round(slope, 2) if 'slope' in locals() else 0,
            'pattern': self._identify_performance_pattern(scores)
        }
    
    def _identify_performance_pattern(self, scores: List[float]) -> str:
        """识别表现模式"""
        if len(scores) < 3:
            return '数据不足'
        
        # 分析前半部分和后半部分
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(scores[mid:]) / (len(scores) - mid) if len(scores) > mid else 0
        
        if second_half_avg > first_half_avg + 5:
            return '后程发力'
        elif first_half_avg > second_half_avg + 5:
            return '开局良好，后续需加强'
        else:
            return '表现稳定'
    
    # 更多辅助方法实现...
    def _identify_section_strengths(self, section: str, answers: List[Dict]) -> List[str]:
        """识别部分优势"""
        strengths = []
        if not answers:
            return strengths
        
        avg_score = sum(a.get('total_score', 0) for a in answers) / len(answers)
        if avg_score > 75:
            strengths.append(f"{section}类问题整体表现优秀")
        
        # 分析具体优势
        high_quality_answers = [a for a in answers if a.get('quality_score', 0) > 80]
        if high_quality_answers:
            strengths.append("回答质量高，逻辑清晰")
        
        fast_responses = [a for a in answers if a.get('response_time_seconds', 300) < 120]
        if len(fast_responses) > len(answers) * 0.6:
            strengths.append("响应迅速，思维敏捷")
        
        return strengths
    
    def _identify_section_weaknesses(self, section: str, answers: List[Dict]) -> List[str]:
        """识别部分弱点"""
        weaknesses = []
        if not answers:
            return weaknesses
        
        avg_score = sum(a.get('total_score', 0) for a in answers) / len(answers)
        if avg_score < 60:
            weaknesses.append(f"{section}类问题需要重点改进")
        
        # 分析具体弱点
        low_completeness = [a for a in answers if a.get('completeness_score', 0) < 60]
        if len(low_completeness) > len(answers) * 0.5:
            weaknesses.append("回答完整性不足")
        
        slow_responses = [a for a in answers if a.get('response_time_seconds', 0) > 300]
        if len(slow_responses) > len(answers) * 0.4:
            weaknesses.append("思考时间较长")
        
        return weaknesses
    
    def _generate_section_improvements(self, section: str, avg_score: float) -> List[str]:
        """生成部分改进建议"""
        suggestions = []
        
        section_specific = {
            'technical': [
                "加强基础技术知识学习",
                "多做编程练习和算法题",
                "学习系统设计和架构知识"
            ],
            'behavioral': [
                "准备STAR格式的经历实例",
                "练习讲述工作经验的技巧",
                "加强团队合作能力展示"
            ],
            'situational': [
                "提高问题分析和解决能力",
                "学习决策制定框架",
                "练习场景化思维"
            ]
        }
        
        if avg_score < 70:
            suggestions.extend(section_specific.get(section, ["需要针对性练习"]))
        
        return suggestions[:3]
    
    def _identify_standout_responses(self, answers: List[Dict]) -> List[Dict]:
        """识别突出回答"""
        if not answers:
            return []
        
        # 找出分数最高的回答
        top_answers = sorted(answers, key=lambda x: x.get('total_score', 0), reverse=True)
        standout = []
        
        for answer in top_answers[:2]:  # 取前两个
            if answer.get('total_score', 0) > 80:
                standout.append({
                    'question_id': answer.get('question_id'),
                    'score': round(answer.get('total_score', 0), 1),
                    'highlights': self._extract_response_highlights(answer)
                })
        
        return standout
    
    def _extract_response_highlights(self, answer: Dict) -> List[str]:
        """提取回答亮点"""
        highlights = []
        
        if answer.get('quality_score', 0) > 85:
            highlights.append("回答质量优秀")
        
        if answer.get('response_time_seconds', 300) < 90:
            highlights.append("响应迅速")
        
        if answer.get('completeness_score', 0) > 85:
            highlights.append("回答完整详细")
        
        if answer.get('word_count', 0) > 100:
            highlights.append("内容丰富")
        
        return highlights
    
    def _generate_question_insights(self, answer: Dict) -> List[str]:
        """生成问题洞察"""
        insights = []
        
        score = answer.get('total_score', 0)
        if score > 85:
            insights.append("表现优秀")
        elif score > 70:
            insights.append("表现良好")
        elif score > 60:
            insights.append("表现一般")
        else:
            insights.append("需要改进")
        
        # 基于具体指标的洞察
        if answer.get('response_time_seconds', 0) > 300:
            insights.append("思考时间较长")
        
        if answer.get('word_count', 0) < 30:
            insights.append("回答较简短")
        
        return insights
    
    # 继续实现其他方法...
    def _generate_key_metrics(self, analysis_result: Dict) -> Dict:
        """生成关键指标"""
        return {
            'overall_score': round(analysis_result['overall_score'], 1),
            'completion_rate': f"{analysis_result['performance_metrics']['completion_rate']:.1%}",
            'average_response_time': f"{analysis_result['performance_metrics'].get('average_response_time', 0):.0f}秒",
            'strongest_area': self._identify_strongest_area(analysis_result),
            'improvement_priority': self._identify_improvement_priority(analysis_result)
        }
    
    def _get_top_recommendations(self, analysis_result: Dict) -> List[str]:
        """获取顶级建议"""
        return analysis_result['recommendations'][:5]
    
    def _identify_strongest_area(self, analysis_result: Dict) -> str:
        """识别最强领域"""
        section_scores = analysis_result['section_scores']
        if not section_scores:
            return "暂无数据"
        
        best_section = max(section_scores.items(), key=lambda x: x[1]['average_score'])
        return f"{best_section[0]} (得分: {best_section[1]['average_score']:.1f})"
    
    def _identify_improvement_priority(self, analysis_result: Dict) -> str:
        """识别改进优先级"""
        section_scores = analysis_result['section_scores']
        if not section_scores:
            return "暂无数据"
        
        weakest_section = min(section_scores.items(), key=lambda x: x[1]['average_score'])
        return f"{weakest_section[0]} (得分: {weakest_section[1]['average_score']:.1f})"
    
    # 其他辅助方法的简化实现
    def _create_session_timeline(self, analysis_result: Dict) -> List[Dict]:
        """创建会话时间线"""
        return [
            {'time': '开始', 'event': '面试开始'},
            {'time': '进行中', 'event': '问题回答'},
            {'time': '结束', 'event': '面试完成'}
        ]
    
    def _find_strength_evidence(self, analysis_result: Dict) -> List[str]:
        """寻找优势证据"""
        return ["基于答案质量和响应时间的综合评估"]
    
    def _suggest_strength_leverage(self, strengths: List[str]) -> List[str]:
        """建议优势利用"""
        return ["继续发挥现有优势", "在弱项改进中运用强项"]
    
    def _assess_weakness_impact(self, weaknesses: List[str]) -> Dict:
        """评估弱点影响"""
        return {'severity': 'medium', 'impact_areas': weaknesses}
    
    def _prioritize_improvements(self, weaknesses: List[str]) -> List[str]:
        """优先级改进"""
        return weaknesses[:3]
    
    def _perform_gap_analysis(self, analysis_result: Dict) -> Dict:
        """执行差距分析"""
        return {
            'current_level': round(analysis_result['overall_score'], 1),
            'target_level': 85,
            'gap': round(85 - analysis_result['overall_score'], 1)
        }
    
    def _create_development_roadmap(self, analysis_result: Dict) -> List[Dict]:
        """创建发展路线图"""
        return [
            {'phase': '短期', 'duration': '1-2个月', 'focus': '基础改进'},
            {'phase': '中期', 'duration': '3-6个月', 'focus': '技能提升'},
            {'phase': '长期', 'duration': '6个月以上', 'focus': '专业发展'}
        ]
    
    def _generate_short_term_goals(self, analysis_result: Dict) -> List[str]:
        """生成短期目标"""
        return ["完善回答结构", "提高响应速度", "增强技术表达"]
    
    def _generate_long_term_development(self, analysis_result: Dict) -> List[str]:
        """生成长期发展"""
        return ["建立专业知识体系", "提升领导力", "发展行业洞察"]
    
    def _suggest_resources(self, analysis_result: Dict) -> List[Dict]:
        """建议资源"""
        return [
            {'type': '书籍', 'name': '面试技巧指南'},
            {'type': '在线课程', 'name': '技术面试准备'},
            {'type': '实践平台', 'name': '模拟面试系统'}
        ]
    
    def _create_practice_plan(self, analysis_result: Dict) -> Dict:
        """创建练习计划"""
        return {
            'daily': '每日技术问题练习 30分钟',
            'weekly': '每周模拟面试 1-2次',
            'monthly': '月度进度评估和调整'
        }
    
    def _generate_specific_observations(self, analysis_result: Dict) -> List[str]:
        """生成具体观察"""
        return ["回答逻辑性良好", "技术理解深度有待提升", "沟通表达清晰"]
    
    def _generate_behavioral_insights(self, analysis_result: Dict) -> List[str]:
        """生成行为洞察"""
        return ["思考方式系统性", "学习能力强", "适应性良好"]
    
    def _assess_communication_style(self, analysis_result: Dict) -> Dict:
        """评估沟通风格"""
        return {
            'style': '直接型',
            'strengths': ['表达清晰', '逻辑性强'],
            'improvements': ['可增加互动性', '适当增加例子']
        }
    
    def _create_action_items(self, analysis_result: Dict) -> List[Dict]:
        """创建行动项目"""
        return [
            {'action': '技术知识复习', 'priority': 'high', 'timeline': '1个月'},
            {'action': '面试技巧练习', 'priority': 'medium', 'timeline': '2个月'}
        ]
    
    def _create_milestone_schedule(self, analysis_result: Dict) -> List[Dict]:
        """创建里程碑计划"""
        return [
            {'milestone': '基础改进完成', 'target_date': '1个月后'},
            {'milestone': '技能提升验证', 'target_date': '3个月后'}
        ]
    
    def _define_success_metrics(self, analysis_result: Dict) -> List[str]:
        """定义成功指标"""
        return ["面试分数提升10分", "技术问题正确率90%", "回答完整性85%"]
    
    def _create_follow_up_plan(self, analysis_result: Dict) -> Dict:
        """创建跟进计划"""
        return {
            'next_assessment': '1个月后',
            'check_points': ['2周后进度检查', '1个月后全面评估'],
            'support_needed': ['技术指导', '面试练习机会']
        }
    
    def _generate_technical_overview(self, analysis_result: Dict) -> Dict:
        """生成技术概览"""
        technical_answers = [
            a for a in analysis_result.get('answer_analysis', [])
            if a.get('question_type') == 'technical'
        ]
        
        if not technical_answers:
            return {'message': '本次面试未包含技术问题'}
        
        tech_scores = [a.get('technical_score', 0) for a in technical_answers]
        avg_tech_score = sum(tech_scores) / len(tech_scores) if tech_scores else 0
        
        return {
            'technical_question_count': len(technical_answers),
            'average_technical_score': round(avg_tech_score, 1),
            'technical_grade': self._get_letter_grade(avg_tech_score),
            'strongest_technical_area': self._identify_strongest_technical_area(technical_answers),
            'technical_consistency': self._calculate_technical_consistency(tech_scores),
            'key_technical_insights': self._extract_technical_insights(technical_answers)
        }
    
    def _generate_skill_assessment(self, analysis_result: Dict) -> Dict:
        """生成技能评估"""
        technical_answers = [
            a for a in analysis_result.get('answer_analysis', [])
            if a.get('question_type') == 'technical'
        ]
        
        skills_assessment = {
            'programming_fundamentals': 0,
            'problem_solving': 0,
            'system_design': 0,
            'best_practices': 0,
            'communication': 0
        }
        
        if technical_answers:
            # 基于关键词和回答质量评估技能
            for answer in technical_answers:
                keywords = answer.get('keywords_found', {})
                quality_score = answer.get('quality_score', 0)
                
                # 编程基础
                if any(word in str(keywords) for word in ['algorithm', 'data structure', 'complexity']):
                    skills_assessment['programming_fundamentals'] += quality_score
                
                # 问题解决
                if any(word in str(keywords) for word in ['problem', 'solution', 'approach']):
                    skills_assessment['problem_solving'] += quality_score
                
                # 系统设计
                if any(word in str(keywords) for word in ['system', 'architecture', 'scalability']):
                    skills_assessment['system_design'] += quality_score
                
                # 最佳实践
                if any(word in str(keywords) for word in ['best practice', 'pattern', 'optimization']):
                    skills_assessment['best_practices'] += quality_score
                
                # 技术沟通
                skills_assessment['communication'] += answer.get('completeness_score', 0)
            
            # 标准化分数
            count = len(technical_answers)
            for skill in skills_assessment:
                skills_assessment[skill] = round(skills_assessment[skill] / count, 1) if count > 0 else 0
        
        return skills_assessment
    
    def _generate_problem_solving_analysis(self, analysis_result: Dict) -> Dict:
        """生成问题解决分析"""
        technical_answers = [
            a for a in analysis_result.get('answer_analysis', [])
            if a.get('question_type') == 'technical'
        ]
        
        if not technical_answers:
            return {'message': '无技术问题解决分析数据'}
        
        problem_solving_metrics = {
            'approach_clarity': 0,
            'solution_completeness': 0,
            'alternative_consideration': 0,
            'time_complexity_awareness': 0,
            'error_handling': 0
        }
        
        for answer in technical_answers:
            answer_text = answer.get('answer_text', '').lower()
            
            # 方法清晰度
            if any(word in answer_text for word in ['approach', 'method', 'strategy', 'first', 'then']):
                problem_solving_metrics['approach_clarity'] += answer.get('quality_score', 0)
            
            # 解决方案完整性
            problem_solving_metrics['solution_completeness'] += answer.get('completeness_score', 0)
            
            # 替代方案考虑
            if any(word in answer_text for word in ['alternative', 'another way', 'also', 'option']):
                problem_solving_metrics['alternative_consideration'] += 20
            
            # 时间复杂度意识
            if any(word in answer_text for word in ['complexity', 'time', 'performance', 'efficient']):
                problem_solving_metrics['time_complexity_awareness'] += 15
            
            # 错误处理
            if any(word in answer_text for word in ['error', 'exception', 'handle', 'validation']):
                problem_solving_metrics['error_handling'] += 10
        
        # 标准化分数
        count = len(technical_answers)
        for metric in problem_solving_metrics:
            problem_solving_metrics[metric] = round(
                problem_solving_metrics[metric] / count, 1
            ) if count > 0 else 0
        
        return {
            'metrics': problem_solving_metrics,
            'overall_problem_solving_score': round(
                sum(problem_solving_metrics.values()) / len(problem_solving_metrics), 1
            ),
            'strengths': self._identify_problem_solving_strengths(problem_solving_metrics),
            'improvement_areas': self._identify_problem_solving_improvements(problem_solving_metrics)
        }
    
    def _generate_technical_recommendations(self, analysis_result: Dict) -> List[str]:
        """生成技术建议"""
        recommendations = []
        
        technical_answers = [
            a for a in analysis_result.get('answer_analysis', [])
            if a.get('question_type') == 'technical'
        ]
        
        if not technical_answers:
            return ["建议增加技术问题练习"]
        
        avg_tech_score = sum(a.get('technical_score', 0) for a in technical_answers) / len(technical_answers)
        
        if avg_tech_score < 60:
            recommendations.extend([
                "加强基础编程概念学习",
                "多做算法和数据结构练习",
                "学习常见设计模式"
            ])
        elif avg_tech_score < 75:
            recommendations.extend([
                "深入学习高级技术概念",
                "练习系统设计问题",
                "关注性能优化技巧"
            ])
        else:
            recommendations.extend([
                "保持技术学习的连续性",
                "关注新技术趋势",
                "考虑技术领导力发展"
            ])
        
        # 基于具体弱点的建议
        avg_completeness = sum(a.get('completeness_score', 0) for a in technical_answers) / len(technical_answers)
        if avg_completeness < 70:
            recommendations.append("提高技术问题回答的完整性")
        
        avg_response_time = sum(a.get('response_time_seconds', 0) for a in technical_answers) / len(technical_answers)
        if avg_response_time > 300:
            recommendations.append("提高技术问题的反应速度")
        
        return recommendations[:8]  # 限制建议数量
    
    # 新增辅助方法
    def _identify_strongest_technical_area(self, technical_answers: List[Dict]) -> str:
        """识别最强技术领域"""
        if not technical_answers:
            return "暂无数据"
        
        # 基于关键词分析最强领域
        area_scores = {
            'algorithms': 0,
            'data_structures': 0,
            'system_design': 0,
            'programming': 0,
            'debugging': 0
        }
        
        for answer in technical_answers:
            keywords = answer.get('keywords_found', {})
            score = answer.get('technical_score', 0)
            
            programming_keywords = keywords.get('programming', [])
            for keyword in programming_keywords:
                if keyword in ['algorithm', 'sort', 'search']:
                    area_scores['algorithms'] += score
                elif keyword in ['array', 'list', 'tree', 'graph']:
                    area_scores['data_structures'] += score
                elif keyword in ['system', 'architecture', 'scalable']:
                    area_scores['system_design'] += score
                elif keyword in ['function', 'class', 'method']:
                    area_scores['programming'] += score
                elif keyword in ['debug', 'test', 'error']:
                    area_scores['debugging'] += score
        
        if not any(area_scores.values()):
            return "编程基础"
        
        strongest_area = max(area_scores.items(), key=lambda x: x[1])
        return strongest_area[0].replace('_', ' ').title()
    
    def _calculate_technical_consistency(self, tech_scores: List[float]) -> str:
        """计算技术一致性"""
        if len(tech_scores) < 2:
            return "数据不足"
        
        variance = sum((score - sum(tech_scores)/len(tech_scores)) ** 2 for score in tech_scores) / len(tech_scores)
        std_dev = variance ** 0.5
        
        if std_dev < 5:
            return "非常稳定"
        elif std_dev < 10:
            return "相对稳定"
        elif std_dev < 15:
            return "有波动"
        else:
            return "波动较大"
    
    def _extract_technical_insights(self, technical_answers: List[Dict]) -> List[str]:
        """提取技术洞察"""
        insights = []
        
        if not technical_answers:
            return insights
        
        avg_quality = sum(a.get('quality_score', 0) for a in technical_answers) / len(technical_answers)
        avg_completeness = sum(a.get('completeness_score', 0) for a in technical_answers) / len(technical_answers)
        avg_response_time = sum(a.get('response_time_seconds', 0) for a in technical_answers) / len(technical_answers)
        
        if avg_quality > 80:
            insights.append("技术回答质量优秀，逻辑清晰")
        elif avg_quality < 60:
            insights.append("技术回答质量有待提升")
        
        if avg_completeness > 80:
            insights.append("技术问题回答完整详细")
        elif avg_completeness < 60:
            insights.append("技术回答可以更加完整")
        
        if avg_response_time < 120:
            insights.append("技术问题反应迅速")
        elif avg_response_time > 300:
            insights.append("技术问题思考时间较长")
        
        # 关键词使用分析
        total_keywords = sum(len(a.get('keywords_found', {}).get('programming', [])) for a in technical_answers)
        if total_keywords > len(technical_answers) * 3:
            insights.append("技术术语使用丰富")
        elif total_keywords < len(technical_answers):
            insights.append("可增加技术术语的使用")
        
        return insights
    
    def _identify_problem_solving_strengths(self, metrics: Dict) -> List[str]:
        """识别问题解决优势"""
        strengths = []
        
        for metric, score in metrics.items():
            if score > 75:
                strength_map = {
                    'approach_clarity': '解决方案思路清晰',
                    'solution_completeness': '解决方案完整',
                    'alternative_consideration': '善于考虑多种方案',
                    'time_complexity_awareness': '性能意识强',
                    'error_handling': '重视错误处理'
                }
                if metric in strength_map:
                    strengths.append(strength_map[metric])
        
        return strengths
    
    def _identify_problem_solving_improvements(self, metrics: Dict) -> List[str]:
        """识别问题解决改进点"""
        improvements = []
        
        for metric, score in metrics.items():
            if score < 60:
                improvement_map = {
                    'approach_clarity': '提高解决方案表述的清晰度',
                    'solution_completeness': '增强解决方案的完整性',
                    'alternative_consideration': '多考虑替代解决方案',
                    'time_complexity_awareness': '增强算法复杂度意识',
                    'error_handling': '重视异常情况处理'
                }
                if metric in improvement_map:
                    improvements.append(improvement_map[metric])
        
        return improvements 