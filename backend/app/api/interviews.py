from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError as MarshmallowValidationError

from app.services.interview_service import InterviewService
from app.services.simple_ai_responder import SimpleAIResponder
from app.services.question_matcher import QuestionMatcher
from app.models.question import InterviewType
from app.utils.exceptions import APIError, ValidationError, NotFoundError
from app.utils.subscription_utils import subscription_required
from datetime import datetime

interviews_bp = Blueprint('interviews', __name__)
interview_service = InterviewService()
question_matcher = QuestionMatcher()

# 验证模式
class CreateInterviewSchema(Schema):
    resume_id = fields.Integer(required=True)
    interview_type = fields.Str(required=True, validate=lambda x: x in ['technical', 'hr', 'comprehensive', 'mock'])
    total_questions = fields.Integer(allow_none=True, validate=lambda x: x is None or (5 <= x <= 20))
    custom_title = fields.Str(allow_none=True)
    difficulty_distribution = fields.Dict(allow_none=True)
    type_distribution = fields.Dict(allow_none=True)

class SubmitAnswerSchema(Schema):
    question_id = fields.Integer(required=True)
    answer_text = fields.Str(allow_none=True)
    response_time = fields.Integer(allow_none=True)

@interviews_bp.route('', methods=['POST'])
@jwt_required()
@subscription_required(feature='interviews', usage_type='interviews')
def create_interview():
    """创建面试会话"""
    try:
        user_id = get_jwt_identity()
        
        # 数据验证
        schema = CreateInterviewSchema()
        data = schema.load(request.get_json() or {})
        
        # 转换面试类型
        interview_type = InterviewType(data['interview_type'])
        
        # 创建面试会话
        session = interview_service.create_interview_session(
            user_id=user_id,
            resume_id=data['resume_id'],
            interview_type=interview_type,
            total_questions=data.get('total_questions', 10),
            difficulty_distribution=data.get('difficulty_distribution'),
            type_distribution=data.get('type_distribution'),
            custom_title=data.get('custom_title')
        )
        
        return jsonify({
            'success': True,
            'message': 'Interview session created successfully',
            'data': {
                'session': session.to_dict(),
                'session_id': session.session_id
            }
        }), 201
        
    except MarshmallowValidationError as e:
        raise APIError('Data validation failed', 422, e.messages)
    except (ValidationError, NotFoundError) as e:
        raise APIError(str(e), 400)
    except Exception as e:
        raise APIError(f'Failed to create interview session: {str(e)}', 500)

@interviews_bp.route('', methods=['GET'])
@jwt_required()  # 重新启用认证
def get_interviews():
    """获取用户的面试会话列表"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取真实的数据库数据
        try:
            sessions_data = interview_service.get_user_interview_sessions(user_id, page, per_page)
            
            return jsonify({
                'success': True,
                'data': sessions_data
            })
            
        except Exception as db_error:
            # 如果数据库查询失败，返回空列表而不是演示数据
            print(f"Database query failed: {db_error}")
            return jsonify({
                'success': True,
                'data': {
                    'sessions': [],
                    'total': 0,
                    'pages': 0,
                    'current_page': page,
                    'per_page': per_page
                }
            })
        
    except Exception as e:
        raise APIError(f'Failed to get interview list: {str(e)}', 500)

# AI回答生成验证模式
class AIAnswerSchema(Schema):
    question = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)

# 问题匹配验证模式
class QuestionMatchSchema(Schema):
    speech_text = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    limit = fields.Integer(allow_none=True, validate=lambda x: x is None or (1 <= x <= 10))

@interviews_bp.route('/generate-answer', methods=['POST'])
@jwt_required()
def generate_ai_answer():
    """根据问题生成AI回答"""
    try:
        user_id = get_jwt_identity()
        
        # 数据验证
        schema = AIAnswerSchema()
        data = schema.load(request.get_json() or {})
        
        question = data['question'].strip()
        
        # 使用简化的AI服务
        ai_responder = SimpleAIResponder()
        answer = ai_responder.generate_answer(question)
        
        return jsonify({
            'success': True,
            'data': {
                'question': question,
                'answer': answer,
                'generated_at': datetime.utcnow().isoformat()
            }
        })
        
    except MarshmallowValidationError as e:
        raise APIError('Data validation failed', 422, e.messages)
    except Exception as e:
        raise APIError(f'Failed to generate AI answer: {str(e)}', 500)

@interviews_bp.route('/<session_id>', methods=['GET'])
@jwt_required()
def get_interview(session_id):
    """获取面试会话详情"""
    try:
        user_id = get_jwt_identity()
        
        session = interview_service.get_interview_session(user_id, session_id)
        questions = interview_service.get_session_questions(user_id, session_id)
        
        return jsonify({
            'success': True,
            'data': {
                'session': session.to_dict(),
                'questions': questions,
                'total_questions': len(questions)
            }
        })
        
    except NotFoundError as e:
        raise APIError(str(e), 404)
    except Exception as e:
        raise APIError(f'Failed to get interview details: {str(e)}', 500)

@interviews_bp.route('/<session_id>/start', methods=['POST'])
@jwt_required()
def start_interview(session_id):
    """开始面试会话"""
    try:
        user_id = int(get_jwt_identity())  # 确保转换为整数
        
        session = interview_service.start_interview_session(user_id, session_id)
        next_question = interview_service.get_next_question(user_id, session_id)
        
        return jsonify({
            'success': True,
            'message': 'Interview started',
            'data': {
                'session': session.to_dict(),
                'next_question': next_question
            }
        })
        
    except (ValidationError, NotFoundError) as e:
        raise APIError(str(e), 400)
    except Exception as e:
        raise APIError(f'Failed to start interview: {str(e)}', 500)

@interviews_bp.route('/<session_id>/next', methods=['GET'])
@jwt_required()
def get_next_question(session_id):
    """获取下一个问题"""
    try:
        user_id = get_jwt_identity()
        
        next_question = interview_service.get_next_question(user_id, session_id)
        
        if next_question is None:
            return jsonify({
                'success': True,
                'data': {
                    'completed': True,
                    'message': 'All questions completed'
                }
            })
        
        return jsonify({
            'success': True,
            'data': next_question
        })
        
    except (ValidationError, NotFoundError) as e:
        raise APIError(str(e), 400)
    except Exception as e:
        raise APIError(f'Failed to get question: {str(e)}', 500)

@interviews_bp.route('/<session_id>/answer', methods=['POST'])
@jwt_required()
def submit_answer(session_id):
    """提交答案"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        user_id = int(get_jwt_identity())  # 确保转换为整数
        logger.info(f"🔍 [API DEBUG] submit_answer called: user_id={user_id}, session_id={session_id}")
        
        # 数据验证
        schema = SubmitAnswerSchema()
        data = schema.load(request.get_json() or {})
        logger.info(f"🔍 [API DEBUG] Request data: {data}")
        
        result = interview_service.submit_answer(
            user_id=user_id,
            session_id=session_id,
            question_id=data['question_id'],
            answer_text=data.get('answer_text'),
            response_time=data.get('response_time')
        )
        
        logger.info(f"✅ [API DEBUG] Answer submitted successfully")
        return jsonify({
            'success': True,
            'message': 'Answer submitted successfully',
            'data': result
        })
        
    except MarshmallowValidationError as e:
        logger.error(f"❌ [API DEBUG] Marshmallow validation error: {e.messages}")
        raise APIError('Data validation failed', 422, e.messages)
    except (ValidationError, NotFoundError) as e:
        logger.error(f"❌ [API DEBUG] Validation/NotFound error: {str(e)}")
        raise APIError(str(e), 400)
    except Exception as e:
        logger.error(f"❌ [API DEBUG] Unexpected error: {str(e)}")
        import traceback
        logger.error(f"❌ [API DEBUG] Traceback: {traceback.format_exc()}")
        raise APIError(f'Failed to submit answer: {str(e)}', 500)

@interviews_bp.route('/<session_id>/end', methods=['POST'])
@jwt_required()
def end_interview(session_id):
    """结束面试会话"""
    try:
        user_id = get_jwt_identity()
        
        session = interview_service.end_interview_session(user_id, session_id)
        
        return jsonify({
            'success': True,
            'message': 'Interview ended',
            'data': {
                'session': session.to_dict()
            }
        })
        
    except NotFoundError as e:
        raise APIError(str(e), 404)
    except Exception as e:
        raise APIError(f'Failed to end interview: {str(e)}', 500)

@interviews_bp.route('/<session_id>/abandon', methods=['PUT'])
@jwt_required()
def abandon_interview(session_id):
    """设置面试会话为已放弃状态"""
    try:
        user_id = int(get_jwt_identity())
        
        # 获取放弃原因
        data = request.get_json() or {}
        reason = data.get('reason', 'user_action')
        
        session = interview_service.abandon_interview_session(user_id, session_id, reason)
        
        return jsonify({
            'success': True,
            'message': 'Interview session abandoned',
            'data': {
                'session': session.to_dict()
            }
        })
        
    except (ValidationError, NotFoundError) as e:
        raise APIError(str(e), 400)
    except Exception as e:
        raise APIError(f'Failed to abandon interview: {str(e)}', 500)

@interviews_bp.route('/<session_id>', methods=['DELETE'])
@jwt_required()
def delete_interview(session_id):
    """删除面试会话"""
    try:
        user_id = get_jwt_identity()
        
        interview_service.delete_interview_session(user_id, session_id)
        
        return jsonify({
            'success': True,
            'message': 'Interview session deleted'
        })
        
    except NotFoundError as e:
        raise APIError(str(e), 404)
    except Exception as e:
        raise APIError(f'Failed to delete interview: {str(e)}', 500)

@interviews_bp.route('/<session_id>/regenerate', methods=['POST'])
@jwt_required()
def regenerate_questions(session_id):
    """重新生成问题"""
    try:
        user_id = get_jwt_identity()
        
        session = interview_service.regenerate_questions(user_id, session_id)
        questions = interview_service.get_session_questions(user_id, session_id)
        
        return jsonify({
            'success': True,
            'message': 'Questions regenerated successfully',
            'data': {
                'session': session.to_dict(),
                'questions': questions,
                'total_questions': len(questions)
            }
        })
        
    except (ValidationError, NotFoundError) as e:
        raise APIError(str(e), 400)
    except Exception as e:
        raise APIError(f'Failed to regenerate questions: {str(e)}', 500)

@interviews_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取面试统计信息"""
    try:
        user_id = get_jwt_identity()
        
        stats = interview_service.get_interview_statistics(user_id)
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        raise APIError(f'Failed to get statistics: {str(e)}', 500)

@interviews_bp.route('/types', methods=['GET'])
def get_interview_types():
    """获取面试类型列表"""
    try:
        types = [
            {
                'value': 'technical',
                'label': 'Technical Interview',
                'description': 'Mainly examines technical skills and programming abilities',
                'question_distribution': {
                    'technical': 6,
                    'experience': 2,
                    'situational': 2
                }
            },
            {
                'value': 'hr',
                'label': 'HR Interview',
                'description': 'Mainly examines behavioral performance and teamwork abilities',
                'question_distribution': {
                    'behavioral': 4,
                    'experience': 3,
                    'situational': 2,
                    'general': 1
                }
            },
            {
                'value': 'comprehensive',
                'label': 'Comprehensive Interview',
                'description': 'Comprehensive assessment of technical and behavioral abilities',
                'question_distribution': {
                    'technical': 3,
                    'behavioral': 3,
                    'experience': 2,
                    'situational': 2
                }
            },
            {
                'value': 'mock',
                'label': 'Mock Interview',
                'description': 'Simulates real interview scenarios to comprehensively practice interview skills',
                'question_distribution': {
                    'behavioral': 3,
                    'technical': 2,
                    'situational': 2,
                    'experience': 1
                }
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'types': types,
                'difficulty_levels': [
                    {'value': 'easy', 'label': 'Easy'},
                    {'value': 'medium', 'label': 'Medium'},
                    {'value': 'hard', 'label': 'Hard'}
                ],
                'question_types': [
                    {'value': 'technical', 'label': 'Technical Questions'},
                    {'value': 'behavioral', 'label': 'Behavioral Questions'},
                    {'value': 'experience', 'label': 'Experience Questions'},
                    {'value': 'situational', 'label': 'Situational Questions'},
                    {'value': 'general', 'label': 'General Questions'}
                ]
            }
        })
        
    except Exception as e:
        raise APIError(f'Failed to get interview types: {str(e)}', 500)

@interviews_bp.route('/match-question', methods=['POST'])
@jwt_required()
def match_historical_question():
    """匹配历史问题"""
    try:
        user_id = get_jwt_identity()
        
        # 数据验证
        schema = QuestionMatchSchema()
        data = schema.load(request.get_json() or {})
        
        speech_text = data['speech_text'].strip()
        limit = data.get('limit', 3)
        
        # 从语音文本中提取问题
        extracted_question = question_matcher.extract_question_from_speech(speech_text)
        
        if not extracted_question:
            return jsonify({
                'success': True,
                'data': {
                    'matches': [],
                    'extracted_question': None,
                    'message': 'No question recognized from speech'
                }
            })
        
        # 查找相似问题
        matches = question_matcher.find_similar_questions(
            user_id=user_id,
            query_text=extracted_question,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': {
                'matches': matches,
                'extracted_question': extracted_question,
                'total_matches': len(matches),
                'speech_text': speech_text
            }
        })
        
    except MarshmallowValidationError as e:
        raise APIError('Data validation failed', 422, e.messages)
    except Exception as e:
        raise APIError(f'Failed to match question: {str(e)}', 500)

@interviews_bp.route('/<session_id>/answers', methods=['GET'])
@jwt_required()
def get_interview_answers(session_id):
    """获取面试会话的所有答案"""
    try:
        user_id = get_jwt_identity()
        
        # 获取面试答案
        answers = interview_service.get_interview_answers(user_id, session_id)
        
        return jsonify({
            'success': True,
            'data': {
                'answers': answers,
                'total': len(answers)
            }
        })
        
    except NotFoundError as e:
        raise APIError(str(e), 404)
    except Exception as e:
        raise APIError(f'Failed to get interview answers: {str(e)}', 500) 