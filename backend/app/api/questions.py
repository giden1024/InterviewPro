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
# from app.tasks.question_tasks import generate_questions_async, generate_ai_reference_async

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

class CreateQuestionSchema(Schema):
    question_text = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    question_type = fields.String(required=True, validate=validate.OneOf(['technical', 'behavioral', 'situational', 'general']))
    difficulty = fields.String(required=True, validate=validate.OneOf(['easy', 'medium', 'hard']))
    category = fields.String(allow_none=True, validate=validate.Length(max=100))
    answer_text = fields.String(required=True, validate=validate.Length(min=1, max=5000))
    tags = fields.List(fields.String(), allow_none=True)

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

@questions_bp.route('/create', methods=['POST'])
@jwt_required()
def create_question():
    """手动创建问题"""
    try:
        user_id = int(get_jwt_identity())
        
        # 验证请求数据
        schema = CreateQuestionSchema()
        data = schema.load(request.get_json() or {})
        
        # 获取用户的最新简历
        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", 404)
        
        # 获取用户的最新简历
        latest_resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.uploaded_at.desc()).first()
        if not latest_resume:
            return error_response("No resume found. Please upload a resume first.", 400)
        
        # 创建或获取一个通用的面试会话
        session_title = f"Manual Questions - {datetime.now().strftime('%Y-%m-%d')}"
        session = InterviewSession.query.filter_by(
            user_id=user_id,
            resume_id=latest_resume.id,
            title=session_title,
            interview_type=InterviewType.COMPREHENSIVE
        ).first()
        
        if not session:
            # 创建新的面试会话
            session_id = str(uuid.uuid4())
            session = InterviewSession(
                user_id=user_id,
                resume_id=latest_resume.id,
                session_id=session_id,
                title=session_title,
                interview_type=InterviewType.COMPREHENSIVE,
                total_questions=0,  # 手动创建的问题不限制数量
                status='ready'
            )
            db.session.add(session)
            db.session.flush()  # 获取session.id
        
        # 创建问题
        question = Question(
            user_id=user_id,
            resume_id=latest_resume.id,
            session_id=session.id,
            question_text=data['question_text'],
            question_type=QuestionType(data['question_type']),
            difficulty=QuestionDifficulty(data['difficulty']),
            category=data.get('category', '通用'),
            tags=data.get('tags', []),
            expected_answer=data['answer_text'],  # 将用户输入的答案作为期望答案
            evaluation_criteria={},
            ai_context={}
        )
        
        db.session.add(question)
        
        # 同时创建一个答案记录
        answer = Answer(
            user_id=user_id,
            question_id=None,  # 将在flush后设置
            session_id=session.id,
            answer_text=data['answer_text'],
            response_time=0,
            score=None,
            ai_feedback=None,
            answered_at=datetime.utcnow()
        )
        
        db.session.flush()  # 获取question.id
        answer.question_id = question.id
        db.session.add(answer)
        
        # 更新会话的问题数量
        session.total_questions += 1
        
        db.session.commit()
        
        return success_response(
            data={
                'question': question.to_dict(),
                'session': session.to_dict()
            },
            message="Question created successfully"
        )
        
    except ValidationError as e:
        return error_response("Validation failed", 422, e.messages)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating question: {e}")
        return error_response("Failed to create question", 500)

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
        
        # 检查会话状态 - 允许created、in_progress和ready状态
        if interview_session.status not in ['created', 'in_progress', 'ready']:
            return error_response("Interview session is not in valid state for question generation", 400)
        
        # 初始化AI问题生成器
        generator = AIQuestionGenerator()
        
        # 生成问题
        questions_data = generator.generate_questions_for_resume(
            resume=resume,
            user_id=user_id,  # 添加用户ID参数
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

@questions_bp.route('/generate-async', methods=['POST'])
@jwt_required()
def generate_questions_async_endpoint():
    """同步生成面试问题（原异步接口改为同步）"""
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
        
        # 查找现有的面试会话
        session_id = data.get('session_id')
        if not session_id:
            return error_response("Session ID is required", 400)
            
        interview_session = InterviewSession.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).first()
        
        if not interview_session:
            return error_response("Interview session not found", 404)
        
        # 检查会话状态 - 允许created、in_progress和ready状态
        if interview_session.status not in ['created', 'in_progress', 'ready']:
            return error_response("Interview session is not in valid state for question generation", 400)
        
        # 准备简历数据
        resume_data = {
            'id': resume.id,
            'user_id': resume.user_id,
            'filename': resume.original_filename,
            'content': resume.content,
            'parsed_data': resume.parsed_data
        }
        
        # 直接调用同步问题生成函数
        from app.services.ai_question_generator import AIQuestionGenerator
        from app.services.question_cache_service import QuestionCacheService
        
        try:
            # 创建问题生成器
            generator = AIQuestionGenerator()
            cache_service = QuestionCacheService()
            
            # 检查缓存
            cache_key = f"questions:{user_id}:{hash(resume.content)}"
            cached_questions = cache_service.get_cached_questions(cache_key)
            
            if cached_questions:
                current_app.logger.info(f"Using cached questions for user {user_id}")
                questions = cached_questions
            else:
                current_app.logger.info(f"Generating new questions for user {user_id}")
                # 生成问题
                questions = generator.generate_questions(
                    resume_data=resume_data,
                    interview_type=interview_session.interview_type.value,
                    total_questions=interview_session.total_questions,
                    difficulty_distribution=interview_session.difficulty_distribution,
                    type_distribution=interview_session.type_distribution
                )
                
                # 缓存问题
                cache_service.cache_questions(cache_key, questions)
            
            # 保存问题到数据库
            saved_questions = []
            for question_data in questions:
                question = Question(
                    resume_id=resume.id,
                    user_id=user_id,
                    session_id=interview_session.session_id,
                    question_text=question_data['content'],
                    question_type=question_data.get('type', 'general'),
                    difficulty=question_data.get('difficulty', 'medium'),
                    category=question_data.get('category', 'general')
                )
                db.session.add(question)
                saved_questions.append(question)
            
            # 更新会话状态
            interview_session.status = 'ready'
            interview_session.questions_generated_at = datetime.utcnow()
            
            db.session.commit()
            
            current_app.logger.info(f"Successfully generated {len(saved_questions)} questions for user {user_id}, session {session_id}")
            
            return success_response(
                data={
                    'session_id': session_id,
                    'questions': questions,
                    'total_questions': len(questions),
                    'status': 'COMPLETED',
                    'message': 'Questions generated successfully'
                },
                message="Questions generated successfully"
            )
            
        except Exception as e:
            current_app.logger.error(f"Error generating questions: {e}")
            db.session.rollback()
            return error_response("Failed to generate questions", 500)
        
    except Exception as e:
        current_app.logger.error(f"Error in generate_questions_async_endpoint: {e}")
        return error_response("Failed to generate questions", 500)

@questions_bp.route('/task-status/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """获取异步任务状态"""
    try:
        user_id = int(get_jwt_identity())
        
        # 获取任务状态
        task = current_app.celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'Task is pending...'
            }
        elif task.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 100),
                'status': task.info.get('status', '')
            }
        elif task.state == 'SUCCESS':
            result = task.result
            if result.get('status') == 'SUCCESS':
                # 保存生成的问题到数据库
                questions_data = result.get('questions', [])
                questions = []
                
                # 查找会话
                session = InterviewSession.query.filter_by(user_id=user_id).order_by(InterviewSession.created_at.desc()).first()
                if session:
                    for q_data in questions_data:
                        question = Question(
                            resume_id=session.resume_id,
                            user_id=user_id,
                            session_id=session.id,
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
                    session.status = 'ready'
                    db.session.commit()
                
                response = {
                    'task_id': task_id,
                    'state': task.state,
                    'status': 'Task completed successfully',
                    'questions': [q.to_dict() for q in questions],
                    'from_cache': result.get('from_cache', False),
                    'generated_at': result.get('generated_at')
                }
            else:
                response = {
                    'task_id': task_id,
                    'state': 'FAILURE',
                    'status': 'Task failed',
                    'error': result.get('error', 'Unknown error')
                }
        else:
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'Task failed',
                'error': str(task.info)
            }
        
        return success_response(data=response)
        
    except Exception as e:
        current_app.logger.error(f"Error getting task status: {e}")
        return error_response("Failed to get task status", 500)

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
        has_answers_param = request.args.get('has_answers')
        
        # 如果has_answers参数为None或未提供，返回所有问题
        if has_answers_param is None:
            # 获取所有问题，包括没有答案的
            questions_query = Question.query.filter_by(user_id=user_id).order_by(Question.created_at.desc())
            total = questions_query.count()
            questions = questions_query.offset((page - 1) * per_page).limit(per_page).all()
            
            result_questions = []
            for question in questions:
                # 获取最新的答案（如果有的话）
                latest_answer = None
                if question.session_id:
                    answer = Answer.query.filter_by(
                        question_id=question.id,
                        user_id=user_id
                    ).order_by(Answer.answered_at.desc()).first()
                    
                    if answer:
                        latest_answer = {
                            'id': answer.id,
                            'answer_text': answer.answer_text,
                            'score': answer.score,
                            'answered_at': answer.answered_at.isoformat()
                        }
                
                question_data = {
                    'id': question.id,
                    'question_text': question.question_text,
                    'question_type': question.question_type.value,
                    'difficulty': question.difficulty.value,
                    'category': question.category or '通用',
                    'tags': question.tags or [],
                    'created_at': question.created_at.isoformat(),
                    'session_id': question.session_id,  # 添加session_id字段
                    'latest_answer': latest_answer
                }
                
                # 获取会话信息（面试类型）
                if question.session_id:
                    session = InterviewSession.query.get(question.session_id)
                    if session:
                        question_data['interview_type'] = session.interview_type.value
                        question_data['session_title'] = session.title
                
                result_questions.append(question_data)
        else:
            # 原有的逻辑：只返回有答案的问题
            has_answers = has_answers_param.lower() == 'true'
            
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
                    'session_id': question.session_id,  # 添加session_id字段
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
            message=f"Successfully retrieved {len(result_questions)} questions"
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
        
        # 获取最新的答案（如果有的话）
        latest_answer = None
        current_app.logger.info(f"Question {question_id} session_id: {question.session_id}")
        
        if question.session_id:
            answer = Answer.query.filter_by(
                question_id=question.id,
                user_id=user_id
            ).order_by(Answer.answered_at.desc()).first()
            
            current_app.logger.info(f"Found answer: {answer}")
            
            if answer:
                latest_answer = {
                    'id': answer.id,
                    'answer_text': answer.answer_text,
                    'score': answer.score,
                    'answered_at': answer.answered_at.isoformat()
                }
                current_app.logger.info(f"Latest answer: {latest_answer}")
        
        question_data['latest_answer'] = latest_answer
        current_app.logger.info(f"Final question_data keys: {list(question_data.keys())}")
        
        return success_response(
            data={'question': question_data},
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
            user_id=user_id,  # 添加用户ID参数
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

# 缓存管理API
@questions_bp.route('/cache/stats', methods=['GET'])
@jwt_required()
def get_cache_stats():
    """获取缓存统计信息"""
    try:
        from app.services.question_cache_service import QuestionCacheService
        
        cache_service = QuestionCacheService()
        stats = cache_service.get_cache_stats()
        
        return success_response(
            data=stats,
            message="Cache statistics retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error getting cache stats: {e}")
        return error_response("Failed to get cache statistics", 500)

@questions_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
def clear_cache():
    """清除缓存"""
    try:
        user_id = int(get_jwt_identity())
        data = request.json or {}
        clear_all = data.get('clear_all', False)
        
        from app.services.question_cache_service import QuestionCacheService
        
        cache_service = QuestionCacheService()
        
        if clear_all:
            # 管理员功能：清除所有缓存
            # 这里可以添加管理员权限检查
            success = cache_service.clear_cache()
            message = "All cache cleared successfully"
        else:
            # 清除当前用户的缓存
            success = cache_service.clear_user_cache(user_id)
            message = f"User {user_id} cache cleared successfully"
        
        if success:
            return success_response(
                data={'cleared': True},
                message=message
            )
        else:
            return error_response("Failed to clear cache", 500)
            
    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {e}")
        return error_response("Failed to clear cache", 500) 

@questions_bp.route('/reference-cache/stats', methods=['GET'])
@jwt_required()
def get_reference_cache_stats():
    """获取AI参考答案缓存统计信息"""
    try:
        from app.extensions import redis_client
        if not redis_client:
            return error_response("Redis not available", 503)
        
        # 获取所有参考答案缓存键
        cache_keys = redis_client.keys("ref_answer:*")
        
        # 统计缓存信息
        cache_stats = {
            'total_cached_answers': len(cache_keys),
            'cache_keys': cache_keys[:10],  # 只显示前10个键
            'cache_size': len(cache_keys)
        }
        
        # 计算缓存命中率（这里需要实际使用数据，暂时返回0）
        cache_stats['estimated_hit_rate'] = 0.0
        
        return success_response(
            data=cache_stats,
            message="Reference answer cache statistics retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error getting reference cache stats: {e}")
        return error_response("Failed to get cache statistics", 500)

@questions_bp.route('/reference-cache/clear', methods=['POST'])
@jwt_required()
def clear_reference_cache():
    """清除AI参考答案缓存"""
    try:
        from app.extensions import redis_client
        if not redis_client:
            return error_response("Redis not available", 503)
        
        # 删除所有参考答案缓存
        cache_keys = redis_client.keys("ref_answer:*")
        if cache_keys:
            redis_client.delete(*cache_keys)
            cleared_count = len(cache_keys)
        else:
            cleared_count = 0
        
        current_app.logger.info(f"Cleared {cleared_count} reference answer cache entries")
        
        return success_response(
            data={'cleared_count': cleared_count},
            message=f"Cleared {cleared_count} reference answer cache entries"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error clearing reference cache: {e}")
        return error_response("Failed to clear cache", 500) 