from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
import uuid
from datetime import datetime

from app.extensions import db
from app.models.question import Question, InterviewSession, QuestionType, QuestionDifficulty, InterviewType
from app.models.resume import Resume
from app.models.user import User
from app.services.ai_question_generator import AIQuestionGenerator
from app.utils.response import success_response, error_response

questions_bp = Blueprint('questions', __name__)

# 验证模式
class GenerateQuestionsSchema(Schema):
    resume_id = fields.Integer(required=True)
    interview_type = fields.String(required=True, validate=validate.OneOf(['technical', 'hr', 'comprehensive']))
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
        
        # 创建面试会话
        session_id = str(uuid.uuid4())
        interview_session = InterviewSession(
            user_id=user_id,
            resume_id=resume.id,
            session_id=session_id,
            title=data.get('title', "AI Generated Interview"),
            interview_type=InterviewType(data['interview_type']),
            total_questions=data.get('total_questions', 10),
            difficulty_distribution=data.get('difficulty_distribution'),
            type_distribution=data.get('type_distribution'),
            status='created'
        )
        
        db.session.add(interview_session)
        db.session.flush()  # 获取session ID
        
        # 初始化AI问题生成器
        generator = AIQuestionGenerator()
        
        # 生成问题
        questions_data = generator.generate_questions_for_resume(
            resume=resume,
            interview_type=InterviewType(data['interview_type']),
            total_questions=data.get('total_questions', 10),
            difficulty_distribution=data.get('difficulty_distribution'),
            type_distribution=data.get('type_distribution')
        )
        
        # 保存生成的问题到数据库
        questions = []
        for q_data in questions_data:
            question = Question(
                resume_id=resume.id,
                user_id=user_id,
                session_id=interview_session.id,  # 关联到会话
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
        
        db.session.commit()
        
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
def get_question_detail():
    """获取特定问题的详细信息"""
    try:
        user_id = int(get_jwt_identity())
        question_id = request.view_args['question_id']
        
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