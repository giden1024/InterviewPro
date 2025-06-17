from app.extensions import db
from datetime import datetime
import enum

class ResumeStatus(enum.Enum):
    """简历处理状态"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class Resume(db.Model):
    """简历模型"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 文件信息
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, docx, doc
    
    # 处理状态
    status = db.Column(db.Enum(ResumeStatus), default=ResumeStatus.UPLOADED, nullable=False)
    error_message = db.Column(db.Text)
    
    # 解析后的内容
    parsed_content = db.Column(db.JSON)  # 存储解析后的结构化数据
    raw_text = db.Column(db.Text)  # 原始文本内容
    
    # 提取的关键信息
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    skills = db.Column(db.JSON)  # 技能列表
    experience = db.Column(db.JSON)  # 工作经历
    education = db.Column(db.JSON)  # 教育背景
    
    # 时间戳
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Resume {self.filename}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'status': self.status.value,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'skills': self.skills or [],
            'experience': self.experience or [],
            'education': self.education or [],
            'error_message': self.error_message
        } 