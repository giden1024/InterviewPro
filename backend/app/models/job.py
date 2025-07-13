from datetime import datetime
from app.extensions import db
from enum import Enum

class JobType(Enum):
    FULL_TIME = 'full-time'
    PART_TIME = 'part-time'
    CONTRACT = 'contract'
    INTERNSHIP = 'internship'
    FREELANCE = 'freelance'

class JobStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ARCHIVED = 'archived'

class Job(db.Model):
    """职位模型"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True)  # 关联的简历
    
    # 基本信息
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    description = db.Column(db.Text)
    requirements = db.Column(db.JSON)  # 职位要求
    responsibilities = db.Column(db.JSON)  # 工作职责
    
    # 薪资和位置
    salary_range = db.Column(db.String(100))
    location = db.Column(db.String(200))
    remote_allowed = db.Column(db.Boolean, default=False)
    
    # 职位类型和状态
    job_type = db.Column(db.Enum(JobType), default=JobType.FULL_TIME)
    status = db.Column(db.Enum(JobStatus), default=JobStatus.ACTIVE)
    
    # 来源信息
    source_url = db.Column(db.String(500))  # 职位链接
    source_type = db.Column(db.String(50))  # url, screenshot, manual
    
    # 解析数据
    parsed_data = db.Column(db.JSON)  # AI解析的结构化数据
    skills_required = db.Column(db.JSON)  # 技能要求
    experience_level = db.Column(db.String(50))  # 经验要求
    
    # 匹配信息
    match_score = db.Column(db.Float)  # 与用户简历的匹配度
    match_details = db.Column(db.JSON)  # 匹配详情
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('jobs', lazy=True))
    resume = db.relationship('Resume', backref=db.backref('jobs', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'salary_range': self.salary_range,
            'location': self.location,
            'remote_allowed': self.remote_allowed,
            'job_type': self.job_type.value if self.job_type else None,
            'status': self.status.value if self.status else None,
            'source_url': self.source_url,
            'source_type': self.source_type,
            'parsed_data': self.parsed_data,
            'skills_required': self.skills_required,
            'experience_level': self.experience_level,
            'match_score': self.match_score,
            'match_details': self.match_details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>' 