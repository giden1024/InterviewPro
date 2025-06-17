"""
Interview Analysis API Routes
面试结果分析API路由
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.question import InterviewSession, Answer, Question
from app.services.interview_analyzer import InterviewAnalyzer
from app.utils.response import success_response, error_response
from datetime import datetime, timedelta
import logging

# 创建蓝图
analysis = Blueprint('analysis', __name__, url_prefix='/api/analysis')
logger = logging.getLogger(__name__)


@analysis.route('/session/<session_id>', methods=['GET'])
@jwt_required()
def analyze_session(session_id):
    """
    分析面试会话结果
    
    Args:
        session_id: 面试会话ID
        
    Returns:
        完整的面试分析结果
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 验证会话存在
        session = InterviewSession.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return error_response("面试会话不存在", 404)
        
        # 确保面试已完成
        if session.status.value not in ['completed', 'paused']:
            return error_response("面试尚未完成，无法进行分析", 400)
        
        # 执行分析
        analyzer = InterviewAnalyzer()
        analysis_result = analyzer.analyze_interview_session(session_id, user_id)
        
        if 'error' in analysis_result:
            return error_response(f"分析失败: {analysis_result['error']}", 500)
        
        return success_response(analysis_result, "面试分析完成")
        
    except Exception as e:
        logger.error(f"面试会话分析失败: {str(e)}")
        return error_response(f"分析失败: {str(e)}", 500)


@analysis.route('/report/<session_id>', methods=['GET'])
@jwt_required()
def generate_report(session_id):
    """
    生成面试报告
    
    Args:
        session_id: 面试会话ID
        
    Returns:
        格式化的面试报告
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取分析结果
        analyzer = InterviewAnalyzer()
        analysis_result = analyzer.analyze_interview_session(session_id, user_id)
        
        if 'error' in analysis_result:
            return error_response(f"报告生成失败: {analysis_result['error']}", 500)
        
        # 生成格式化报告
        report = _format_interview_report(analysis_result)
        
        return success_response(report, "面试报告生成成功")
        
    except Exception as e:
        logger.error(f"面试报告生成失败: {str(e)}")
        return error_response(f"报告生成失败: {str(e)}", 500)


@analysis.route('/visualization/<session_id>', methods=['GET'])
@jwt_required()
def get_visualization_data(session_id):
    """
    获取可视化数据
    
    Args:
        session_id: 面试会话ID
        
    Returns:
        可视化图表数据
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取分析结果
        analyzer = InterviewAnalyzer()
        analysis_result = analyzer.analyze_interview_session(session_id, user_id)
        
        if 'error' in analysis_result:
            return error_response(f"可视化数据获取失败: {analysis_result['error']}", 500)
        
        # 返回可视化数据
        viz_data = analysis_result.get('visualization_data', {})
        
        return success_response(viz_data, "可视化数据获取成功")
        
    except Exception as e:
        logger.error(f"可视化数据获取失败: {str(e)}")
        return error_response(f"数据获取失败: {str(e)}", 500)


@analysis.route('/statistics', methods=['GET'])
@jwt_required()
def get_user_statistics():
    """
    获取用户面试统计数据
    
    Returns:
        用户的整体面试统计
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取时间范围参数
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 查询用户的面试会话
        sessions = InterviewSession.query.filter(
            InterviewSession.user_id == user_id,
            InterviewSession.created_at >= start_date,
            InterviewSession.status.in_(['completed', 'paused'])
        ).all()
        
        if not sessions:
            return success_response({
                'total_interviews': 0,
                'average_score': 0,
                'improvement_trend': [],
                'performance_by_type': {},
                'time_distribution': {}
            }, "暂无面试数据")
        
        # 计算统计数据
        stats = _calculate_user_statistics(sessions, user_id)
        
        return success_response(stats, "统计数据获取成功")
        
    except Exception as e:
        logger.error(f"统计数据获取失败: {str(e)}")
        return error_response(f"统计数据获取失败: {str(e)}", 500)


@analysis.route('/comparison', methods=['POST'])
@jwt_required()
def compare_interviews():
    """
    比较多个面试结果
    
    Returns:
        面试结果对比分析
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        session_ids = data.get('session_ids', [])
        if len(session_ids) < 2:
            return error_response("至少需要两个面试会话进行比较", 400)
        
        if len(session_ids) > 5:
            return error_response("最多只能比较5个面试会话", 400)
        
        # 验证所有会话都属于该用户
        sessions = InterviewSession.query.filter(
            InterviewSession.session_id.in_(session_ids),
            InterviewSession.user_id == user_id
        ).all()
        
        if len(sessions) != len(session_ids):
            return error_response("部分面试会话不存在或无权访问", 404)
        
        # 执行比较分析
        comparison_result = _compare_interview_sessions(session_ids, user_id)
        
        return success_response(comparison_result, "面试比较分析完成")
        
    except Exception as e:
        logger.error(f"面试比较分析失败: {str(e)}")
        return error_response(f"比较分析失败: {str(e)}", 500)


@analysis.route('/insights/<session_id>', methods=['GET'])
@jwt_required()
def get_detailed_insights(session_id):
    """
    获取详细的面试洞察
    
    Args:
        session_id: 面试会话ID
        
    Returns:
        详细的面试分析洞察
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取基础分析
        analyzer = InterviewAnalyzer()
        analysis_result = analyzer.analyze_interview_session(session_id, user_id)
        
        if 'error' in analysis_result:
            return error_response(f"洞察分析失败: {analysis_result['error']}", 500)
        
        # 生成深度洞察
        insights = _generate_detailed_insights(analysis_result, session_id, user_id)
        
        return success_response(insights, "详细洞察分析完成")
        
    except Exception as e:
        logger.error(f"详细洞察分析失败: {str(e)}")
        return error_response(f"洞察分析失败: {str(e)}", 500)


@analysis.route('/export/<session_id>', methods=['GET'])
@jwt_required()
def export_analysis(session_id):
    """
    导出面试分析结果
    
    Args:
        session_id: 面试会话ID
        
    Returns:
        可导出的面试分析数据
    """
    try:
        user_id = int(get_jwt_identity())
        export_format = request.args.get('format', 'json')
        
        # 获取分析结果
        analyzer = InterviewAnalyzer()
        analysis_result = analyzer.analyze_interview_session(session_id, user_id)
        
        if 'error' in analysis_result:
            return error_response(f"导出失败: {analysis_result['error']}", 500)
        
        # 格式化导出数据
        export_data = _format_export_data(analysis_result, export_format)
        
        return success_response(export_data, f"面试分析数据导出成功({export_format})")
        
    except Exception as e:
        logger.error(f"面试分析导出失败: {str(e)}")
        return error_response(f"导出失败: {str(e)}", 500)


# 辅助函数
def _format_interview_report(analysis_result):
    """格式化面试报告"""
    report = {
        'report_id': f"report_{analysis_result['session_info']['session_id']}",
        'generated_at': datetime.utcnow().isoformat(),
        'session_summary': {
            'title': analysis_result['session_info']['title'],
            'type': analysis_result['session_info']['interview_type'],
            'duration': analysis_result['session_info']['duration_minutes'],
            'completion_rate': analysis_result['performance_metrics']['completion_rate']
        },
        'performance_overview': {
            'overall_score': round(analysis_result['overall_score'], 1),
            'grade': _get_performance_grade(analysis_result['overall_score']),
            'ranking_percentile': _calculate_percentile(analysis_result['overall_score'])
        },
        'section_performance': {},
        'key_findings': {
            'strengths': analysis_result['strengths'],
            'areas_for_improvement': analysis_result['weaknesses'],
            'recommendations': analysis_result['recommendations']
        },
        'detailed_analysis': analysis_result['detailed_feedback'],
        'next_steps': analysis_result['detailed_feedback'].get('next_steps', [])
    }
    
    # 格式化各部分表现
    for section, scores in analysis_result['section_scores'].items():
        report['section_performance'][section] = {
            'score': round(scores['average_score'], 1),
            'grade': _get_performance_grade(scores['average_score']),
            'question_count': scores['count'],
            'best_score': round(scores['max_score'], 1),
            'lowest_score': round(scores['min_score'], 1)
        }
    
    return report


def _calculate_user_statistics(sessions, user_id):
    """计算用户统计数据"""
    analyzer = InterviewAnalyzer()
    stats = {
        'total_interviews': len(sessions),
        'average_score': 0,
        'improvement_trend': [],
        'performance_by_type': {},
        'time_distribution': {},
        'score_distribution': {
            'excellent': 0,
            'good': 0,
            'average': 0,
            'below_average': 0
        }
    }
    
    # 收集所有分析结果
    analysis_results = []
    for session in sessions:
        try:
            result = analyzer.analyze_interview_session(session.session_id, user_id)
            if 'error' not in result:
                analysis_results.append(result)
        except Exception:
            continue
    
    if not analysis_results:
        return stats
    
    # 计算平均分
    scores = [result['overall_score'] for result in analysis_results]
    stats['average_score'] = round(sum(scores) / len(scores), 1)
    
    # 改进趋势
    sorted_results = sorted(analysis_results, 
                          key=lambda x: x['session_info']['start_time'] or '')
    stats['improvement_trend'] = [
        {
            'date': result['session_info']['start_time'][:10] if result['session_info']['start_time'] else '',
            'score': round(result['overall_score'], 1)
        }
        for result in sorted_results[-10:]  # 最近10次
    ]
    
    # 按类型分析
    type_scores = {}
    for result in analysis_results:
        interview_type = result['session_info']['interview_type']
        if interview_type not in type_scores:
            type_scores[interview_type] = []
        type_scores[interview_type].append(result['overall_score'])
    
    for interview_type, type_score_list in type_scores.items():
        stats['performance_by_type'][interview_type] = {
            'average_score': round(sum(type_score_list) / len(type_score_list), 1),
            'count': len(type_score_list),
            'best_score': round(max(type_score_list), 1)
        }
    
    # 分数分布
    for score in scores:
        if score >= 90:
            stats['score_distribution']['excellent'] += 1
        elif score >= 75:
            stats['score_distribution']['good'] += 1
        elif score >= 60:
            stats['score_distribution']['average'] += 1
        else:
            stats['score_distribution']['below_average'] += 1
    
    return stats


def _compare_interview_sessions(session_ids, user_id):
    """比较多个面试会话"""
    analyzer = InterviewAnalyzer()
    comparison = {
        'sessions': [],
        'comparison_metrics': {},
        'improvement_analysis': {},
        'recommendations': []
    }
    
    # 获取所有分析结果
    analysis_results = []
    for session_id in session_ids:
        try:
            result = analyzer.analyze_interview_session(session_id, user_id)
            if 'error' not in result:
                analysis_results.append(result)
        except Exception:
            continue
    
    if len(analysis_results) < 2:
        return {'error': '无法获取足够的分析数据进行比较'}
    
    # 基础比较数据
    for result in analysis_results:
        session_summary = {
            'session_id': result['session_info']['session_id'],
            'title': result['session_info']['title'],
            'type': result['session_info']['interview_type'],
            'date': result['session_info']['start_time'][:10] if result['session_info']['start_time'] else '',
            'overall_score': round(result['overall_score'], 1),
            'completion_rate': result['performance_metrics']['completion_rate'],
            'duration': result['session_info']['duration_minutes']
        }
        comparison['sessions'].append(session_summary)
    
    # 比较指标
    scores = [result['overall_score'] for result in analysis_results]
    comparison['comparison_metrics'] = {
        'score_range': {
            'highest': round(max(scores), 1),
            'lowest': round(min(scores), 1),
            'difference': round(max(scores) - min(scores), 1)
        },
        'average_score': round(sum(scores) / len(scores), 1),
        'consistency': round(100 - (max(scores) - min(scores)), 1)  # 一致性指标
    }
    
    # 改进分析
    if len(analysis_results) > 1:
        latest_score = analysis_results[-1]['overall_score']
        earliest_score = analysis_results[0]['overall_score']
        comparison['improvement_analysis'] = {
            'trend': 'improving' if latest_score > earliest_score else 'declining' if latest_score < earliest_score else 'stable',
            'improvement_rate': round(latest_score - earliest_score, 1),
            'best_performance': max(analysis_results, key=lambda x: x['overall_score'])['session_info']['session_id']
        }
    
    return comparison


def _generate_detailed_insights(analysis_result, session_id, user_id):
    """生成详细洞察"""
    insights = {
        'performance_insights': [],
        'behavioral_patterns': [],
        'technical_assessment': {},
        'time_management': {},
        'communication_effectiveness': {},
        'growth_opportunities': []
    }
    
    overall_score = analysis_result['overall_score']
    answer_analysis = analysis_result.get('answer_analysis', [])
    
    # 表现洞察
    if overall_score >= 85:
        insights['performance_insights'].append("展现出色的面试技能，回答质量始终保持高水准")
    elif overall_score >= 70:
        insights['performance_insights'].append("面试表现良好，在某些领域有突出表现")
    else:
        insights['performance_insights'].append("面试表现有较大提升空间，建议重点关注基础技能")
    
    # 行为模式分析
    if answer_analysis:
        avg_response_time = sum(a.get('response_time_seconds', 0) for a in answer_analysis) / len(answer_analysis)
        if avg_response_time < 120:
            insights['behavioral_patterns'].append("回答速度较快，思维敏捷")
        elif avg_response_time > 300:
            insights['behavioral_patterns'].append("思考时间较长，偏向深度思考")
        
        # 答案长度分析
        avg_word_count = sum(a.get('word_count', 0) for a in answer_analysis) / len(answer_analysis)
        if avg_word_count > 80:
            insights['behavioral_patterns'].append("回答详细充实，善于表达")
        elif avg_word_count < 30:
            insights['behavioral_patterns'].append("回答较为简洁，可适当增加细节")
    
    # 技术评估
    tech_scores = []
    for analysis in answer_analysis:
        if analysis.get('question_type') == 'technical':
            tech_scores.append(analysis.get('technical_score', 0))
    
    if tech_scores:
        insights['technical_assessment'] = {
            'average_score': round(sum(tech_scores) / len(tech_scores), 1),
            'consistency': len([s for s in tech_scores if abs(s - sum(tech_scores)/len(tech_scores)) < 10]) / len(tech_scores),
            'strength_areas': _identify_technical_strengths(answer_analysis),
            'improvement_areas': _identify_technical_weaknesses(answer_analysis)
        }
    
    return insights


def _format_export_data(analysis_result, export_format):
    """格式化导出数据"""
    export_data = {
        'metadata': {
            'export_format': export_format,
            'export_date': datetime.utcnow().isoformat(),
            'session_id': analysis_result['session_info']['session_id']
        },
        'summary': {
            'overall_score': analysis_result['overall_score'],
            'session_info': analysis_result['session_info'],
            'performance_metrics': analysis_result['performance_metrics']
        },
        'detailed_results': {
            'section_scores': analysis_result['section_scores'],
            'answer_analysis': analysis_result['answer_analysis'],
            'strengths': analysis_result['strengths'],
            'weaknesses': analysis_result['weaknesses'],
            'recommendations': analysis_result['recommendations']
        }
    }
    
    if export_format == 'csv':
        # 为CSV格式准备平铺数据
        export_data['csv_data'] = _flatten_for_csv(analysis_result)
    
    return export_data


# 辅助函数
def _get_performance_grade(score):
    """获取表现等级"""
    if score >= 90:
        return 'A+'
    elif score >= 85:
        return 'A'
    elif score >= 80:
        return 'A-'
    elif score >= 75:
        return 'B+'
    elif score >= 70:
        return 'B'
    elif score >= 65:
        return 'B-'
    elif score >= 60:
        return 'C+'
    elif score >= 55:
        return 'C'
    else:
        return 'D'


def _calculate_percentile(score):
    """计算百分位排名（模拟）"""
    # 简化版百分位计算
    if score >= 90:
        return 95
    elif score >= 80:
        return 85
    elif score >= 70:
        return 70
    elif score >= 60:
        return 50
    else:
        return 25


def _identify_technical_strengths(answer_analysis):
    """识别技术优势"""
    strengths = []
    for analysis in answer_analysis:
        if (analysis.get('question_type') == 'technical' and 
            analysis.get('technical_score', 0) > 80):
            keywords = analysis.get('keywords_found', {})
            for category, words in keywords.items():
                if words:
                    strengths.extend(words[:2])  # 取前两个关键词
    return list(set(strengths))[:5]


def _identify_technical_weaknesses(answer_analysis):
    """识别技术弱点"""
    weaknesses = []
    for analysis in answer_analysis:
        if (analysis.get('question_type') == 'technical' and 
            analysis.get('technical_score', 0) < 60):
            # 基于缺乏的技术关键词识别弱点
            if analysis.get('word_count', 0) < 50:
                weaknesses.append("回答深度不足")
            if not analysis.get('keywords_found', {}):
                weaknesses.append("技术词汇使用较少")
    return list(set(weaknesses))[:3]


def _flatten_for_csv(analysis_result):
    """为CSV导出平铺数据"""
    flattened = []
    
    # 基础信息
    session_info = analysis_result['session_info']
    base_row = {
        'session_id': session_info['session_id'],
        'interview_type': session_info['interview_type'],
        'title': session_info['title'],
        'overall_score': analysis_result['overall_score'],
        'completion_rate': analysis_result['performance_metrics']['completion_rate']
    }
    
    # 每个答案一行
    for analysis in analysis_result.get('answer_analysis', []):
        row = base_row.copy()
        row.update({
            'question_id': analysis['question_id'],
            'question_type': analysis['question_type'],
            'question_difficulty': analysis['question_difficulty'],
            'answer_score': analysis['total_score'],
            'response_time': analysis['response_time_seconds'],
            'word_count': analysis['word_count']
        })
        flattened.append(row)
    
    return flattened 