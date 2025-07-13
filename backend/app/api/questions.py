from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
import uuid
from datetime import datetime

from app.extensions import db
from app.models.question import Question, InterviewSession, QuestionType, QuestionDifficulty, InterviewType, Answer
from app.models.resume import Resume
from app.models.user import User
from app.services.ai_question_generator import AIQuestionGenerator
from app.utils.response import success_response, error_response

questions_bp = Blueprint('questions', __name__)

# 验证模式
class GenerateQuestionsSchema(Schema):
    resume_id = fields.Integer(required=True)
    session_id = fields.String(required=True)  # 现在必须提供session_id
    interview_type = fields.String(allow_none=True, validate=validate.OneOf(['technical', 'hr', 'comprehensive']))  # 改为可选
    total_questions = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=50))
    difficulty_distribution = fields.Dict(allow_none=True)
    type_distribution = fields.Dict(allow_none=True)
    title = fields.String(allow_none=True)

class GetQuestionsSchema(Schema):
    session_id = fields.String(required=True)

# API 端点实现
@questions_bp.route('', methods=['GET'])
@jwt_required()
def get_questions():
    """获取用户的问题列表"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # 分页查询用户的问题
        questions_query = Question.query.filter_by(user_id=user_id).order_by(Question.created_at.desc())
        questions_paginated = questions_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        questions = [q.to_dict() for q in questions_paginated.items]
        
        return success_response(
            data={
                'questions': questions,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': questions_paginated.total,
                    'pages': questions_paginated.pages,
                    'has_next': questions_paginated.has_next,
                    'has_prev': questions_paginated.has_prev
                }
            },
            message=f"Successfully retrieved {len(questions)} questions"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving questions: {e}")
        return error_response("Failed to retrieve questions", 500)

@questions_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_questions():
    """基于简历生成面试问题"""
    try:
        user_id = int(get_jwt_identity())
        
        # 验证请求数据
        schema = GenerateQuestionsSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return error_response("Invalid request data", 400, details=err.messages)
        
        # 检查简历是否存在且属于当前用户
        resume = Resume.query.filter_by(id=data['resume_id'], user_id=user_id).first()
        if not resume:
            return error_response("Resume not found", 404)
        
        if resume.status.value != 'processed':
            return error_response("Resume is not processed yet", 400)
        
        # 查找现有的面试会话（由interviews API创建）
        session_id = data.get('session_id')
        if not session_id:
            return error_response("Session ID is required", 400)
            
        interview_session = InterviewSession.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).first()
        
        if not interview_session:
            return error_response("Interview session not found", 404)
        
        # 检查会话状态
        if interview_session.status != 'created':
            return error_response("Interview session is not in created state", 400)
        
        # 初始化AI问题生成器
        generator = AIQuestionGenerator()
        
        # 生成问题
        questions_data = generator.generate_questions_for_resume(
            resume=resume,
            interview_type=interview_session.interview_type,
            total_questions=interview_session.total_questions,
            difficulty_distribution=interview_session.difficulty_distribution,
            type_distribution=interview_session.type_distribution
        )
        
        # 保存生成的问题到数据库
        questions = []
        for q_data in questions_data:
            question = Question(
                resume_id=resume.id,
                user_id=user_id,
                session_id=interview_session.id,
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                difficulty=q_data['difficulty'],
                category=q_data.get('category', ''),
                tags=q_data.get('tags', []),
                expected_answer=q_data.get('expected_answer', ''),
                evaluation_criteria=q_data.get('evaluation_criteria', {}),
                ai_context=q_data.get('ai_context', {})
            )
            questions.append(question)
            db.session.add(question)
        
        # 更新会话状态
        interview_session.status = 'ready'
        db.session.commit()
        
        current_app.logger.info(f"Generated {len(questions)} questions for user {user_id}, session {session_id}")
        
        return success_response(
            data={
                'session': interview_session.to_dict(),
                'questions': [q.to_dict() for q in questions],
                'stats': {
                    'total_generated': len(questions),
                    'resume_id': resume.id,
                    'resume_filename': resume.original_filename
                }
            },
            message=f"Successfully generated {len(questions)} questions"
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating questions: {e}")
        return error_response("Failed to generate questions", 500)

@questions_bp.route('/session/<session_id>', methods=['GET'])
@jwt_required()
def get_session_questions(session_id):
    """获取特定会话的问题"""
    try:
        user_id = int(get_jwt_identity())
        
        # 查找会话
        session = InterviewSession.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return error_response("Interview session not found", 404)
        
        # 获取会话的问题
        questions = Question.query.filter_by(
            session_id=session.id
        ).order_by(Question.created_at.asc()).all()
        
        return success_response(
            data={
                'session': session.to_dict(),
                'questions': [q.to_dict() for q in questions],
                'total_questions': len(questions)
            },
            message="Session questions retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving session questions: {e}")
        return error_response("Failed to retrieve session questions", 500)

@questions_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_interview_sessions():
    """获取用户的面试会话列表"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # 分页查询会话
        sessions_query = InterviewSession.query.filter_by(user_id=user_id).order_by(
            InterviewSession.created_at.desc()
        )
        sessions_paginated = sessions_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        sessions = []
        for session in sessions_paginated.items:
            session_data = session.to_dict()
            # 添加简历信息
            resume = Resume.query.get(session.resume_id)
            if resume:
                session_data['resume'] = {
                    'id': resume.id,
                    'filename': resume.original_filename,
                    'name': resume.name
                }
            sessions.append(session_data)
        
        return success_response(
            data={
                'sessions': sessions,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': sessions_paginated.total,
                    'pages': sessions_paginated.pages,
                    'has_next': sessions_paginated.has_next,
                    'has_prev': sessions_paginated.has_prev
                }
            },
            message=f"Successfully retrieved {len(sessions)} interview sessions"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving interview sessions: {e}")
        return error_response("Failed to retrieve interview sessions", 500)

@questions_bp.route('/with-answers', methods=['GET'])
@jwt_required()
def get_questions_with_answers():
    """获取用户的问题和答案列表（用于主页显示）"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        has_answers = request.args.get('has_answers', 'true').lower() == 'true'
        
        # 构建查询：获取用户回答过的问题
        query = db.session.query(Question, Answer).join(
            Answer, Question.id == Answer.question_id
        ).filter(
            Question.user_id == user_id,
            Answer.user_id == user_id
        )
        
        # 如果只要有答案的问题
        if has_answers:
            query = query.filter(Answer.answer_text.isnot(None))
        
        # 按回答时间降序排列（最新回答的在前）
        query = query.order_by(Answer.answered_at.desc())
        
        # 分页
        total = query.count()
        questions_with_answers = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # 构建返回数据
        result_questions = []
        for question, answer in questions_with_answers:
            question_data = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type.value,
                'difficulty': question.difficulty.value,
                'category': question.category or '通用',
                'tags': question.tags or [],
                'created_at': question.created_at.isoformat(),
                'latest_answer': {
                    'id': answer.id,
                    'answer_text': answer.answer_text,
                    'score': answer.score,
                    'answered_at': answer.answered_at.isoformat()
                }
            }
            
            # 获取会话信息（面试类型）
            if question.session_id:
                session = InterviewSession.query.get(question.session_id)
                if session:
                    question_data['interview_type'] = session.interview_type.value
                    question_data['session_title'] = session.title
            
            result_questions.append(question_data)
        
        # 如果没有真实数据，返回空列表而不是演示数据
        if not result_questions:
            current_app.logger.info(f"No answered questions found for user {user_id}")
        
        return success_response(
            data={
                'questions': result_questions,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page if total > 0 else 0,
                    'has_next': (page * per_page) < total,
                    'has_prev': page > 1
                }
            },
            message=f"Successfully retrieved {len(result_questions)} questions with answers"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving questions with answers: {e}")
        return error_response("Failed to retrieve questions with answers", 500)

@questions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_question_stats():
    """获取问题生成统计信息"""
    try:
        user_id = int(get_jwt_identity())
        
        # 统计数据
        total_questions = Question.query.filter_by(user_id=user_id).count()
        total_sessions = InterviewSession.query.filter_by(user_id=user_id).count()
        
        # 按类型统计
        type_stats = {}
        for q_type in QuestionType:
            count = Question.query.filter_by(user_id=user_id, question_type=q_type).count()
            type_stats[q_type.value] = count
        
        # 按难度统计
        difficulty_stats = {}
        for difficulty in QuestionDifficulty:
            count = Question.query.filter_by(user_id=user_id, difficulty=difficulty).count()
            difficulty_stats[difficulty.value] = count
        
        # 最近活动
        recent_sessions = InterviewSession.query.filter_by(user_id=user_id).order_by(
            InterviewSession.created_at.desc()
        ).limit(5).all()
        
        return success_response(
            data={
                'total_questions': total_questions,
                'total_sessions': total_sessions,
                'type_distribution': type_stats,
                'difficulty_distribution': difficulty_stats,
                'recent_sessions': [session.to_dict() for session in recent_sessions]
            },
            message="Question statistics retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving question stats: {e}")
        return error_response("Failed to retrieve question statistics", 500)

@questions_bp.route('/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_detail(question_id):
    """获取特定问题的详细信息"""
    try:
        user_id = int(get_jwt_identity())
        
        question = Question.query.filter_by(id=question_id, user_id=user_id).first()
        if not question:
            return error_response("Question not found", 404)
        
        # 获取相关简历信息
        resume = Resume.query.get(question.resume_id)
        question_data = question.to_dict()
        if resume:
            question_data['resume'] = {
                'id': resume.id,
                'filename': resume.original_filename,
                'name': resume.name
            }
        
        return success_response(
            data=question_data,
            message="Question details retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving question detail: {e}")
        return error_response("Failed to retrieve question details", 500)

@questions_bp.route('/test-generator', methods=['POST'])
@jwt_required()
def test_question_generator():
    """测试AI问题生成器（开发和调试用）"""
    try:
        if not current_app.config.get('DEBUG'):
            return error_response("Test endpoint only available in debug mode", 403)
        
        user_id = int(get_jwt_identity())
        data = request.json or {}
        
        # 创建测试简历数据
        test_resume = type('TestResume', (), {
            'id': 0,
            'name': data.get('name', 'Test Candidate'),
            'skills': data.get('skills', ['Python', 'JavaScript', 'React', 'Flask']),
            'experience': data.get('experience', [
                {'title': 'Software Engineer', 'company': 'Tech Corp'},
                {'title': 'Developer', 'company': 'Startup Inc'}
            ]),
            'education': data.get('education', [
                {'degree': 'Computer Science', 'university': 'University'}
            ]),
            'raw_text': data.get('raw_text', 'Test candidate with software development experience')
        })
        
        # 生成测试问题
        generator = AIQuestionGenerator()
        questions_data = generator.generate_questions_for_resume(
            resume=test_resume,
            interview_type=InterviewType(data.get('interview_type', 'comprehensive')),
            total_questions=data.get('total_questions', 5)
        )
        
        return success_response(
            data={
                'test_resume': {
                    'name': test_resume.name,
                    'skills': test_resume.skills,
                    'experience': test_resume.experience
                },
                'generated_questions': questions_data,
                'stats': {
                    'total_generated': len(questions_data),
                    'ai_config': current_app.config.get('AI_QUESTION_CONFIG', {})
                }
            },
            message=f"Test generation completed with {len(questions_data)} questions"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in test question generator: {e}")
        return error_response("Test question generation failed", 500)

@questions_bp.route('/<int:question_id>/generate-reference', methods=['POST'])
@jwt_required()
def generate_ai_reference_answer(question_id):
    """实时生成问题的AI参考答案"""
    try:
        user_id = int(get_jwt_identity())
        
        # 获取问题
        question = Question.query.filter_by(id=question_id, user_id=user_id).first()
        if not question:
            return error_response("Question not found", 404)
        
        # 获取关联的简历信息
        resume = Resume.query.get(question.resume_id)
        if not resume:
            return error_response("Resume not found", 404)
        
        # 初始化AI生成器
        generator = AIQuestionGenerator()
        
        # 生成AI参考答案
        try:
            request_data = request.get_json(silent=True) or {}
        except:
            request_data = {}
        
        reference_answer = generator.generate_reference_answer(
            question=question,
            resume=resume,
            user_context=request_data.get('user_context', {})
        )
        
        current_app.logger.info(f"Generated AI reference answer for question {question_id}")
        
        return success_response(
            data={
                'question_id': question_id,
                'question_text': question.question_text,
                'ai_reference_answer': reference_answer,
                'generated_at': datetime.now().isoformat(),
                'generation_context': {
                    'question_type': question.question_type.value,
                    'difficulty': question.difficulty.value,
                    'category': question.category
                }
            },
            message="AI reference answer generated successfully"
        )
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error generating AI reference answer: {e}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return error_response(f"Failed to generate AI reference answer: {str(e)}", 500)

@questions_bp.route('/batch-generate-references', methods=['POST'])
@jwt_required()
def batch_generate_ai_references():
    """批量生成多个问题的AI参考答案"""
    try:
        user_id = int(get_jwt_identity())
        data = request.json or {}
        question_ids = data.get('question_ids', [])
        
        if not question_ids:
            return error_response("No question IDs provided", 400)
        
        # 验证问题存在且属于当前用户
        questions = Question.query.filter(
            Question.id.in_(question_ids),
            Question.user_id == user_id
        ).all()
        
        if len(questions) != len(question_ids):
            return error_response("Some questions not found or access denied", 404)
        
        # 获取简历信息
        resume_ids = list(set(q.resume_id for q in questions))
        resumes = {r.id: r for r in Resume.query.filter(Resume.id.in_(resume_ids)).all()}
        
        # 初始化AI生成器
        generator = AIQuestionGenerator()
        
        # 批量生成参考答案
        results = []
        for question in questions:
            try:
                resume = resumes.get(question.resume_id)
                if resume:
                    reference_answer = generator.generate_reference_answer(
                        question=question,
                        resume=resume,
                        user_context=data.get('user_context', {})
                    )
                    
                    results.append({
                        'question_id': question.id,
                        'question_text': question.question_text,
                        'ai_reference_answer': reference_answer,
                        'status': 'success'
                    })
                else:
                    results.append({
                        'question_id': question.id,
                        'status': 'error',
                        'error': 'Resume not found'
                    })
            except Exception as e:
                results.append({
                    'question_id': question.id,
                    'status': 'error',
                    'error': str(e)
                })
        
        current_app.logger.info(f"Batch generated AI reference answers for {len(results)} questions")
        
        return success_response(
            data={
                'results': results,
                'total_processed': len(results),
                'successful': len([r for r in results if r.get('status') == 'success']),
                'failed': len([r for r in results if r.get('status') == 'error']),
                'generated_at': datetime.now().isoformat()
            },
            message=f"Processed {len(results)} questions for AI reference generation"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in batch generating AI references: {e}")
        return error_response("Failed to batch generate AI references", 500) 