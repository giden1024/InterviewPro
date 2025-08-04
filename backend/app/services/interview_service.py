import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.resume import Resume
from app.models.question import Question, InterviewSession, QuestionType, QuestionDifficulty, InterviewType
from app.services.ai_question_generator import AIQuestionGenerator
from app.utils.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)

class InterviewService:
    """面试服务"""
    
    def __init__(self):
        """初始化服务"""
        self.ai_generator = AIQuestionGenerator()
    
    def create_interview_session(
        self,
        user_id: int,
        resume_id: int,
        interview_type: InterviewType = InterviewType.COMPREHENSIVE,
        total_questions: int = 10,
        difficulty_distribution: Optional[Dict[str, int]] = None,
        type_distribution: Optional[Dict[str, int]] = None,
        custom_title: Optional[str] = None
    ) -> InterviewSession:
        """
        创建面试会话并生成问题
        
        Args:
            user_id: 用户ID
            resume_id: 简历ID
            interview_type: 面试类型
            total_questions: 总问题数
            difficulty_distribution: 难度分布
            type_distribution: 类型分布
            custom_title: 自定义标题
            
        Returns:
            创建的面试会话
        """
        try:
            # 验证简历是否存在且属于用户
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            if not resume:
                raise NotFoundError("Resume not found or access denied")
            
            if resume.status.value != 'processed':
                raise ValidationError("Resume parsing not completed, unable to generate interview questions")
            
            # 设置默认分布
            if difficulty_distribution is None:
                difficulty_distribution = {"easy": 3, "medium": 5, "hard": 2}
            if type_distribution is None:
                type_distribution = self._get_default_type_distribution(interview_type)
            
            # 生成会话ID和标题
            session_id = str(uuid.uuid4())
            title = custom_title or self._generate_session_title(resume, interview_type)
            
            # 创建面试会话（不立即生成问题）
            session = InterviewSession(
                user_id=user_id,
                resume_id=resume_id,
                session_id=session_id,
                title=title,
                interview_type=interview_type,
                total_questions=total_questions,
                difficulty_distribution=difficulty_distribution,
                type_distribution=type_distribution,
                status='created'  # 明确设置为created状态，等待问题生成
            )
            
            db.session.add(session)
            db.session.commit()
            
            logger.info(f"Successfully created interview session {session_id}, waiting for question generation")
            return session
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database operation failed: {e}")
            raise ValidationError("Failed to create interview session")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create interview session: {e}")
            raise
    
    def get_interview_session(self, user_id: int, session_id: str) -> InterviewSession:
        """获取面试会话"""
        session = None
        
        # 首先尝试按UUID查找（session_id字段）
        session = InterviewSession.query.filter_by(
            session_id=session_id, 
            user_id=user_id
        ).first()
        
        # 如果没找到，且传入的是数字字符串，则按主键ID查找
        if not session and session_id.isdigit():
            session = InterviewSession.query.filter_by(
                id=int(session_id),
                user_id=user_id
            ).first()
        
        if not session:
            raise NotFoundError("Interview session not found or access denied")
        
        return session
    
    def get_user_interview_sessions(
        self, 
        user_id: int, 
        page: int = 1, 
        per_page: int = 10
    ) -> Dict[str, Any]:
        """获取用户的面试会话列表"""
        pagination = InterviewSession.query.filter_by(user_id=user_id)\
            .order_by(InterviewSession.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'sessions': [session.to_dict() for session in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    
    def get_session_questions(
        self, 
        user_id: int, 
        session_id: str,
        include_answers: bool = False
    ) -> List[Dict[str, Any]]:
        """获取面试会话的问题列表"""
        session = self.get_interview_session(user_id, session_id)
        
        # 修复：按session.id正确过滤问题
        questions = Question.query.filter_by(
            session_id=session.id,  # 使用session.id而不是resume_id
            user_id=user_id
        ).order_by(Question.created_at).all()
        
        result = []
        for question in questions:
            q_dict = question.to_dict()
            if include_answers:
                # TODO: 添加答案信息
                pass
            result.append(q_dict)
        
        return result
    
    def start_interview_session(self, user_id: int, session_id: str) -> InterviewSession:
        """开始面试会话"""
        try:
            logger.info(f"Starting interview session {session_id} for user {user_id}")
            
            # 使用数据库锁防止并发问题
            # 确保user_id是整数类型
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            session = db.session.query(InterviewSession).filter_by(
                session_id=session_id,  # 使用session_id字段而不是id字段
                user_id=user_id_int
            ).with_for_update().first()
            
            if not session:
                logger.error(f"Interview session {session_id} not found for user {user_id}")
                raise ValidationError("Interview session not found")
            
            logger.info(f"Found session {session_id} with status: {session.status}")
            
            # 修复：允许 created 和 ready 状态的会话启动，禁止 abandoned 状态
            if session.status not in ['created', 'ready', 'in_progress']:
                if session.status == 'abandoned':
                    logger.error(f"Cannot start abandoned interview session: {session.status}")
                    raise ValidationError("Interview session has been abandoned and cannot be started")
                else:
                    logger.error(f"Invalid session status for starting: {session.status}")
                    raise ValidationError(f"Interview session already started or completed. Current status: {session.status}")
            
            # 如果会话已经是in_progress状态，直接返回
            if session.status == 'in_progress':
                logger.info(f"Session {session_id} is already in progress, returning existing session")
                return session
            
            # 只有created和ready状态才需要实际启动
            session.status = 'in_progress'
            session.started_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"User {user_id} successfully started interview session {session_id}")
            return session
            
        except ValidationError:
            # ValidationError应该直接抛出，不需要回滚
            raise
        except Exception as e:
            logger.error(f"Unexpected error starting interview session {session_id}: {str(e)}")
            db.session.rollback()
            raise ValidationError(f"Failed to start interview session: {str(e)}")
    
    def get_next_question(
        self, 
        user_id: int, 
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取下一个问题"""
        session = self.get_interview_session(user_id, session_id)
        
        if session.status not in ['in_progress']:
            raise ValidationError("Interview session not started or already ended")
        
        questions = self.get_session_questions(user_id, session_id)
        
        if session.current_question_index >= len(questions):
            return None  # 所有问题已完成
        
        current_question = questions[session.current_question_index]
        return {
            'question': current_question,
            'current_index': session.current_question_index,
            'total_questions': len(questions),
            'progress': (session.current_question_index + 1) / len(questions) * 100
        }
    
    def submit_answer(
        self, 
        user_id: int, 
        session_id: str, 
        question_id: int,
        answer_text: Optional[str] = None,
        answer_audio_path: Optional[str] = None,
        response_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """提交答案"""
        from app.models.question import Answer
        
        logger.info(f"🔍 [SERVICE DEBUG] submit_answer called: user_id={user_id}, session_id={session_id}, question_id={question_id}")
        
        try:
            session = self.get_interview_session(user_id, session_id)
            logger.info(f"🔍 [SERVICE DEBUG] Found session: id={session.id}, status={session.status}")
        except Exception as e:
            logger.error(f"❌ [SERVICE DEBUG] Failed to get session: {e}")
            raise
        
        # 修正：允许ready和created状态的会话接收答案，并自动启动会话，禁止abandoned状态
        if session.status in ['ready', 'created']:
            session.status = 'in_progress'
            session.started_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"🔍 [SERVICE DEBUG] Session auto-started from {session.status}")
        elif session.status == 'abandoned':
            logger.error(f"❌ [SERVICE DEBUG] Cannot submit answer to abandoned session: {session.status}")
            raise ValidationError("Interview session has been abandoned and cannot accept answers")
        elif session.status != 'in_progress':
            logger.error(f"❌ [SERVICE DEBUG] Invalid session status: {session.status}")
            raise ValidationError("Interview session not started or already ended")
        
        # 修改：更宽松的问题查找策略
        # 首先尝试严格匹配
        question = Question.query.filter_by(
            id=question_id, 
            user_id=user_id,
            session_id=session.id
        ).first()
        
        logger.info(f"🔍 [SERVICE DEBUG] Strict question query result: {'Found' if question else 'Not found'}")
        
        # 如果严格匹配失败，尝试宽松匹配并自动修复关联
        if not question:
            logger.info(f"🔍 [SERVICE DEBUG] Trying loose question query...")
            question = Question.query.filter_by(
                id=question_id,
                user_id=user_id
            ).first()
            
            if question:
                logger.info(f"🔍 [SERVICE DEBUG] Found question with loose query, fixing association")
                # 自动修复session关联
                old_session_id = question.session_id
                question.session_id = session.id
                db.session.commit()
                logger.info(f"🔍 [SERVICE DEBUG] Fixed session association: {old_session_id} -> {session.id}")
            else:
                logger.error(f"❌ [SERVICE DEBUG] Question not found even with loose query")
        
        if not question:
            logger.error(f"❌ [SERVICE DEBUG] Final validation failed")
            raise ValidationError("Question not found, access denied, or does not belong to current interview session")
        
        logger.info(f"🔍 [SERVICE DEBUG] Using question: id={question.id}")
        
        try:
            # 检查是否已有答案
            existing_answer = Answer.query.filter_by(
                question_id=question_id,
                user_id=user_id
            ).first()
            
            if existing_answer:
                logger.info(f"🔍 [SERVICE DEBUG] Updating existing answer")
                # 更新现有答案
                existing_answer.answer_text = answer_text
                existing_answer.answer_audio_path = answer_audio_path
                existing_answer.response_time = response_time
                existing_answer.updated_at = datetime.utcnow()
                answer = existing_answer
            else:
                logger.info(f"🔍 [SERVICE DEBUG] Creating new answer")
                # 创建新答案
                answer = Answer(
                    session_id=session.id,  # 添加session_id
                    question_id=question_id,
                    user_id=user_id,
                    answer_text=answer_text,
                    answer_audio_path=answer_audio_path,
                    response_time=response_time
                )
                db.session.add(answer)
            
            db.session.commit()
            logger.info(f"✅ [SERVICE DEBUG] Answer saved successfully")
            
            return {
                'answer_id': answer.id,
                'question_id': question_id,
                'submitted_at': answer.created_at.isoformat() if hasattr(answer, 'created_at') else datetime.utcnow().isoformat(),
                'message': 'Answer submitted successfully'
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"❌ [SERVICE DEBUG] Database error: {e}")
            raise ValidationError(f"Failed to save answer: {str(e)}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ [SERVICE DEBUG] Unexpected error: {e}")
            raise ValidationError(f"Error occurred while submitting answer: {str(e)}")
    
    def end_interview_session(self, user_id: int, session_id: str) -> InterviewSession:
        """结束面试会话"""
        session = self.get_interview_session(user_id, session_id)
        
        if session.status == 'completed':
            return session
        
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"User {user_id} ended interview session {session_id}")
        return session
    
    def abandon_interview_session(self, user_id: int, session_id: str, reason: str = 'user_action') -> InterviewSession:
        """设置面试会话为已放弃状态"""
        try:
            logger.info(f"Abandoning interview session {session_id} for user {user_id}, reason: {reason}")
            
            # 确保user_id是整数类型
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            session = db.session.query(InterviewSession).filter_by(
                session_id=session_id,
                user_id=user_id_int
            ).with_for_update().first()
            
            if not session:
                logger.error(f"Interview session {session_id} not found for user {user_id}")
                raise ValidationError("Interview session not found")
            
            logger.info(f"Found session {session_id} with status: {session.status}")
            
            # 检查当前状态，已完成或已放弃的会话不能再次设置为放弃
            if session.status in ['completed', 'abandoned']:
                logger.warning(f"Session {session_id} already in final state: {session.status}")
                return session
            
            # 设置为abandoned状态
            session.status = 'abandoned'
            session.updated_at = datetime.utcnow()
            # 设置完成时间，即使是放弃状态也需要记录结束时间
            session.completed_at = datetime.utcnow()
            
            # 如果会话还没有started_at时间，设置它（用于统计）
            if not session.started_at:
                session.started_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"User {user_id} abandoned interview session {session_id} (reason: {reason})")
            return session
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error abandoning interview session {session_id}: {str(e)}")
            db.session.rollback()
            raise ValidationError(f"Failed to abandon interview session: {str(e)}")
    
    def delete_interview_session(self, user_id: int, session_id: str) -> bool:
        """删除面试会话"""
        from app.models.question import Answer
        
        session = self.get_interview_session(user_id, session_id)
        
        try:
            from sqlalchemy import text
            
            # 使用原生SQL删除，完全避免SQLAlchemy的级联更新问题
            # 1. 删除相关答案
            db.session.execute(
                text("DELETE FROM answers WHERE session_id = :session_id AND user_id = :user_id"),
                {'session_id': session.id, 'user_id': user_id}
            )
            
            # 2. 删除相关问题
            db.session.execute(
                text("DELETE FROM questions WHERE session_id = :session_id AND user_id = :user_id"),
                {'session_id': session.id, 'user_id': user_id}
            )
            
            # 3. 删除面试会话
            db.session.execute(
                text("DELETE FROM interview_sessions WHERE id = :session_id AND user_id = :user_id"),
                {'session_id': session.id, 'user_id': user_id}
            )
            
            db.session.commit()
            
            logger.info(f"User {user_id} deleted interview session {session_id}")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to delete interview session: {e}")
            raise ValidationError("Failed to delete interview session")
    
    def get_interview_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取用户面试统计信息"""
        total_sessions = InterviewSession.query.filter_by(user_id=user_id).count()
        completed_sessions = InterviewSession.query.filter_by(
            user_id=user_id, 
            status='completed'
        ).count()
        
        in_progress_sessions = InterviewSession.query.filter_by(
            user_id=user_id, 
            status='in_progress'
        ).count()
        
        # 最近的面试会话
        recent_sessions = InterviewSession.query.filter_by(user_id=user_id)\
            .order_by(InterviewSession.created_at.desc())\
            .limit(5)\
            .all()
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'in_progress_sessions': in_progress_sessions,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'recent_sessions': [session.to_dict() for session in recent_sessions]
        }
    
    def regenerate_questions(
        self, 
        user_id: int, 
        session_id: str,
        question_types: Optional[List[str]] = None
    ) -> InterviewSession:
        """重新生成问题"""
        session = self.get_interview_session(user_id, session_id)
        
        if session.status != 'created':
            raise ValidationError("Can only regenerate questions for unstarted interview sessions")
        
        # 删除现有问题
        Question.query.filter_by(resume_id=session.resume_id, user_id=user_id).delete()
        
        # 获取简历
        resume = Resume.query.get(session.resume_id)
        
        # 重新生成问题
        questions_data = self.ai_generator.generate_questions_for_resume(
            resume=resume,
            user_id=user_id,  # 添加用户ID参数
            interview_type=session.interview_type,
            total_questions=session.total_questions,
            difficulty_distribution=session.difficulty_distribution,
            type_distribution=session.type_distribution
        )
        
        # 保存新问题
        for q_data in questions_data:
            # 确保枚举值正确转换
            question_type_raw = q_data['question_type']
            if hasattr(question_type_raw, 'value'):
                # 如果是枚举对象，取其值
                question_type_final = question_type_raw.value
            elif isinstance(question_type_raw, str) and '.' in question_type_raw:
                # 如果是字符串形式的枚举（如'QuestionType.TECHNICAL'），提取值部分并转换为小写
                enum_value = question_type_raw.split('.')[-1]
                question_type_final = enum_value.lower()
            else:
                question_type_final = question_type_raw
            
            difficulty_raw = q_data['difficulty']
            if hasattr(difficulty_raw, 'value'):
                # 如果是枚举对象，取其值
                difficulty_final = difficulty_raw.value
            elif isinstance(difficulty_raw, str) and '.' in difficulty_raw:
                # 如果是字符串形式的枚举（如'QuestionDifficulty.MEDIUM'），提取值部分并转换为小写
                enum_value = difficulty_raw.split('.')[-1]
                difficulty_final = enum_value.lower()
            else:
                difficulty_final = difficulty_raw
                
            question = Question(
                resume_id=session.resume_id,
                user_id=user_id,
                session_id=session.id,
                question_text=q_data['question_text'],
                question_type=QuestionType(question_type_final),  # 转换为枚举对象
                difficulty=QuestionDifficulty(difficulty_final),  # 转换为枚举对象
                category=q_data.get('category', ''),
                tags=q_data.get('tags', []),
                ai_context=q_data.get('ai_context', {}),
                expected_answer=q_data.get('expected_answer', ''),
                evaluation_criteria=q_data.get('evaluation_criteria', {})
            )
            db.session.add(question)
        
        db.session.commit()
        
        logger.info(f"为会话 {session_id} 重新生成了问题")
        return session
    
    def _get_default_type_distribution(self, interview_type: InterviewType) -> Dict[str, int]:
        """获取默认问题类型分布"""
        distributions = {
            InterviewType.TECHNICAL: {
                "technical": 6,
                "experience": 2,
                "situational": 2
            },
            InterviewType.HR: {
                "behavioral": 4,
                "experience": 3,
                "situational": 2,
                "general": 1
            },
            InterviewType.COMPREHENSIVE: {
                "technical": 3,
                "behavioral": 3,
                "experience": 2,
                "situational": 2
            },
            InterviewType.MOCK: {
                "behavioral": 3,
                "technical": 2,
                "situational": 2,
                "experience": 1
            }
        }
        return distributions.get(interview_type, distributions[InterviewType.COMPREHENSIVE])
    
    def _generate_session_title(self, resume: Resume, interview_type: InterviewType) -> str:
        """生成会话标题"""
        name = resume.name or "Candidate"
        type_names = {
            InterviewType.TECHNICAL: "Technical Interview",
            InterviewType.HR: "HR Interview",
            InterviewType.COMPREHENSIVE: "Comprehensive Interview",
            InterviewType.MOCK: "Mock Interview"
        }
        type_name = type_names.get(interview_type, "Interview")
        
        return f"{name} - {type_name} ({datetime.now().strftime('%Y-%m-%d')})"
    
    def get_interview_answers(self, user_id: int, session_id: str) -> List[Dict[str, Any]]:
        """获取面试会话的所有答案"""
        from app.models.question import Answer, Question
        
        try:
            # 获取面试会话
            session = self.get_interview_session(user_id, session_id)
            
            # 获取该会话的所有答案，并通过JOIN获取问题信息
            answers_with_questions = db.session.query(Answer, Question).join(
                Question, Answer.question_id == Question.id
            ).filter(
                Answer.session_id == session.id,
                Answer.user_id == user_id
            ).order_by(Question.created_at).all()
            
            result = []
            for answer, question in answers_with_questions:
                answer_dict = {
                    'id': answer.id,
                    'question_id': answer.question_id,
                    'answer_text': answer.answer_text,
                    'score': answer.score,
                    'response_time': answer.response_time,
                    'answered_at': answer.answered_at.isoformat() if answer.answered_at else None,
                    'ai_feedback': answer.ai_feedback or {}
                }
                
                # 添加问题信息
                if question:
                    answer_dict['question'] = {
                        'id': question.id,
                        'question_text': question.question_text,
                        'question_type': question.question_type.value if question.question_type else None,
                        'difficulty': question.difficulty.value if question.difficulty else None
                    }
                
                result.append(answer_dict)
            
            logger.info(f"Retrieved {len(result)} answers, user {user_id}, session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to retrieve interview answers: {e}")
            raise 