from app.extensions import db
from datetime import datetime
import enum

class QuestionType(enum.Enum):
    """问题类型"""
    TECHNICAL = "technical"           # 技术问题
    BEHAVIORAL = "behavioral"         # 行为问题
    EXPERIENCE = "experience"         # 经验问题
    SITUATIONAL = "situational"       # 情景问题
    GENERAL = "general"              # 通用问题

class QuestionDifficulty(enum.Enum):
    """问题难度"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class InterviewType(enum.Enum):
    """面试类型"""
    TECHNICAL = "technical"           # 技术面试
    HR = "hr"                        # HR面试
    COMPREHENSIVE = "comprehensive"   # 综合面试
    MOCK = "mock"                    # 模拟面试

class Question(db.Model):
    """面试问题模型"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=True)  # 关联面试会话
    
    # 问题内容
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum(QuestionType), nullable=False)
    difficulty = db.Column(db.Enum(QuestionDifficulty), nullable=False)
    
    # 问题元数据
    category = db.Column(db.String(100))  # 具体分类，如"Python"、"项目管理"等
    tags = db.Column(db.JSON)  # 标签列表
    
    # AI生成相关
    ai_context = db.Column(db.JSON)  # AI生成时使用的上下文信息
    expected_answer = db.Column(db.Text)  # 期望答案/参考答案
    evaluation_criteria = db.Column(db.JSON)  # 评估标准
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:50]}...>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type.value,
            'difficulty': self.difficulty.value,
            'category': self.category,
            'tags': self.tags or [],
            'expected_answer': self.expected_answer,
            'evaluation_criteria': self.evaluation_criteria or {},
            'ai_context': self.ai_context or {},
            'created_at': self.created_at.isoformat(),
            'session_id': self.session_id
        }

class InterviewSession(db.Model):
    """面试会话模型"""
    __tablename__ = 'interview_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    
    # 会话信息
    session_id = db.Column(db.String(100), unique=True, nullable=False)  # UUID
    title = db.Column(db.String(200), nullable=False)
    interview_type = db.Column(db.Enum(InterviewType), nullable=False)
    
    # 配置信息
    total_questions = db.Column(db.Integer, default=10)
    difficulty_distribution = db.Column(db.JSON)  # 难度分布 {"easy": 3, "medium": 5, "hard": 2}
    type_distribution = db.Column(db.JSON)  # 类型分布
    
    # 状态信息
    status = db.Column(db.String(50), default='created')  # created, ready, in_progress, completed, abandoned
    current_question_index = db.Column(db.Integer, default=0)
    
    # 结果统计
    total_score = db.Column(db.Float)
    completed_questions = db.Column(db.Integer, default=0)
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<InterviewSession {self.session_id}: {self.title}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'interview_type': self.interview_type.value,
            'total_questions': self.total_questions,
            'difficulty_distribution': self.difficulty_distribution,
            'type_distribution': self.type_distribution,
            'status': self.status,
            'current_question_index': self.current_question_index,
            'total_score': self.total_score,
            'completed_questions': self.completed_questions,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

# 在InterviewSession定义后添加关系
InterviewSession.questions = db.relationship('Question', backref='session', lazy='dynamic')
InterviewSession.answers = db.relationship('Answer', backref='session', lazy='dynamic')

class Answer(db.Model):
    """用户答案模型"""
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 答案内容
    answer_text = db.Column(db.Text)
    answer_audio_path = db.Column(db.String(500))  # 音频文件路径
    
    # 评估结果
    score = db.Column(db.Float)  # 0-100分
    ai_feedback = db.Column(db.JSON)  # AI评估反馈
    
    # 时间信息
    response_time = db.Column(db.Integer)  # 回答用时（秒）
    answered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Answer {self.id}: Q{self.question_id}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'score': self.score,
            'ai_feedback': self.ai_feedback or {},
            'response_time': self.response_time,
            'answered_at': self.answered_at.isoformat()
        } 