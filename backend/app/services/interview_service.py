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
                raise NotFoundError("简历不存在或无权限访问")
            
            if resume.status.value != 'processed':
                raise ValidationError("简历尚未解析完成，无法生成面试问题")
            
            # 设置默认分布
            if difficulty_distribution is None:
                difficulty_distribution = {"easy": 3, "medium": 5, "hard": 2}
            if type_distribution is None:
                type_distribution = self._get_default_type_distribution(interview_type)
            
            # 生成会话ID和标题
            session_id = str(uuid.uuid4())
            title = custom_title or self._generate_session_title(resume, interview_type)
            
            # 创建面试会话
            session = InterviewSession(
                user_id=user_id,
                resume_id=resume_id,
                session_id=session_id,
                title=title,
                interview_type=interview_type,
                total_questions=total_questions,
                difficulty_distribution=difficulty_distribution,
                type_distribution=type_distribution
            )
            
            db.session.add(session)
            db.session.flush()  # 获取session.id
            
            # 生成问题
            questions_data = self.ai_generator.generate_questions_for_resume(
                resume=resume,
                interview_type=interview_type,
                total_questions=total_questions,
                difficulty_distribution=difficulty_distribution,
                type_distribution=type_distribution
            )
            
            # 保存问题到数据库
            questions = []
            for i, q_data in enumerate(questions_data):
                question = Question(
                    resume_id=resume_id,
                    user_id=user_id,
                    question_text=q_data['question_text'],
                    question_type=q_data['question_type'],
                    difficulty=q_data['difficulty'],
                    category=q_data.get('category', ''),
                    tags=q_data.get('tags', []),
                    ai_context=q_data.get('ai_context', {}),
                    expected_answer=q_data.get('expected_answer', ''),
                    evaluation_criteria=q_data.get('evaluation_criteria', {})
                )
                questions.append(question)
                db.session.add(question)
            
            db.session.commit()
            
            logger.info(f"成功创建面试会话 {session_id}，生成 {len(questions)} 个问题")
            return session
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise ValidationError("创建面试会话失败")
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建面试会话失败: {e}")
            raise
    
    def get_interview_session(self, user_id: int, session_id: str) -> InterviewSession:
        """获取面试会话"""
        session = InterviewSession.query.filter_by(
            session_id=session_id, 
            user_id=user_id
        ).first()
        
        if not session:
            raise NotFoundError("面试会话不存在或无权限访问")
        
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
        
        questions = Question.query.filter_by(
            resume_id=session.resume_id, 
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
        session = self.get_interview_session(user_id, session_id)
        
        if session.status != 'created':
            raise ValidationError("面试会话已开始或已完成")
        
        session.status = 'in_progress'
        session.started_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"用户 {user_id} 开始面试会话 {session_id}")
        return session
    
    def get_next_question(
        self, 
        user_id: int, 
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取下一个问题"""
        session = self.get_interview_session(user_id, session_id)
        
        if session.status not in ['in_progress']:
            raise ValidationError("面试会话未开始或已结束")
        
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
        
        session = self.get_interview_session(user_id, session_id)
        
        if session.status != 'in_progress':
            raise ValidationError("面试会话未开始或已结束")
        
        # 验证问题
        question = Question.query.filter_by(
            id=question_id, 
            user_id=user_id
        ).first()
        
        if not question:
            raise NotFoundError("问题不存在或无权限访问")
        
        # 创建答案记录
        answer = Answer(
            session_id=session.id,
            question_id=question_id,
            user_id=user_id,
            answer_text=answer_text,
            answer_audio_path=answer_audio_path,
            response_time=response_time
        )
        
        db.session.add(answer)
        
        # 更新会话进度
        session.current_question_index += 1
        session.completed_questions += 1
        
        # 检查是否完成所有问题
        questions = self.get_session_questions(user_id, session_id)
        if session.current_question_index >= len(questions):
            session.status = 'completed'
            session.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"用户 {user_id} 提交了问题 {question_id} 的答案")
        
        return {
            'answer_id': answer.id,
            'next_question': self.get_next_question(user_id, session_id) if session.status == 'in_progress' else None,
            'session_completed': session.status == 'completed'
        }
    
    def end_interview_session(self, user_id: int, session_id: str) -> InterviewSession:
        """结束面试会话"""
        session = self.get_interview_session(user_id, session_id)
        
        if session.status == 'completed':
            return session
        
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"用户 {user_id} 结束面试会话 {session_id}")
        return session
    
    def delete_interview_session(self, user_id: int, session_id: str) -> bool:
        """删除面试会话"""
        session = self.get_interview_session(user_id, session_id)
        
        try:
            # 删除相关的问题和答案（通过级联删除）
            db.session.delete(session)
            db.session.commit()
            
            logger.info(f"用户 {user_id} 删除面试会话 {session_id}")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"删除面试会话失败: {e}")
            raise ValidationError("删除面试会话失败")
    
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
            raise ValidationError("只能为未开始的面试会话重新生成问题")
        
        # 删除现有问题
        Question.query.filter_by(resume_id=session.resume_id, user_id=user_id).delete()
        
        # 获取简历
        resume = Resume.query.get(session.resume_id)
        
        # 重新生成问题
        questions_data = self.ai_generator.generate_questions_for_resume(
            resume=resume,
            interview_type=session.interview_type,
            total_questions=session.total_questions,
            difficulty_distribution=session.difficulty_distribution,
            type_distribution=session.type_distribution
        )
        
        # 保存新问题
        for q_data in questions_data:
            question = Question(
                resume_id=session.resume_id,
                user_id=user_id,
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                difficulty=q_data['difficulty'],
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
            }
        }
        return distributions.get(interview_type, distributions[InterviewType.COMPREHENSIVE])
    
    def _generate_session_title(self, resume: Resume, interview_type: InterviewType) -> str:
        """生成会话标题"""
        name = resume.name or "候选人"
        type_names = {
            InterviewType.TECHNICAL: "技术面试",
            InterviewType.HR: "HR面试",
            InterviewType.COMPREHENSIVE: "综合面试"
        }
        type_name = type_names.get(interview_type, "面试")
        
        return f"{name} - {type_name} ({datetime.now().strftime('%Y-%m-%d')})" 