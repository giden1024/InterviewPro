import os
from datetime import timedelta

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'interview-genius-secret-key-2024'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///interview_genius.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    
    # AI模型配置
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or 'sk-f33bab4e7cef421e8739c295670cb15c'
    
    # 国际化配置 - Internationalization Configuration
    QUESTION_LANGUAGE = os.environ.get('QUESTION_LANGUAGE', 'english')  # 支持: 'english', 'chinese'
    DEFAULT_LOCALE = os.environ.get('DEFAULT_LOCALE', 'en_US')
    SUPPORTED_LANGUAGES = ['en', 'zh', 'es', 'fr', 'de', 'ja', 'ko']  # 支持的语言列表
    
    # 面试问题配置 - Interview Question Configuration
    AI_QUESTION_CONFIG = {
        'language': QUESTION_LANGUAGE,
        'cultural_neutrality': True,  # 确保问题文化中性
        'professional_tone': True,   # 使用专业语调
        'international_friendly': True,  # 适合国际候选人
        'avoid_colloquialisms': True,    # 避免俚语和方言
        'clear_instructions': True       # 提供清晰的指示
    }
    
    # API配置
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev_interview_genius.db'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'dev')
    
    # 开发环境国际化配置
    QUESTION_LANGUAGE = 'english'  # 开发环境默认使用英文
    AI_QUESTION_CONFIG = {
        **Config.AI_QUESTION_CONFIG,
        'debug_mode': True,
        'log_ai_responses': True
    }

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/interview_genius'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/app/uploads'
    
    # 生产环境国际化配置
    QUESTION_LANGUAGE = os.environ.get('QUESTION_LANGUAGE', 'english')
    AI_QUESTION_CONFIG = {
        **Config.AI_QUESTION_CONFIG,
        'cache_questions': True,      # 生产环境启用问题缓存
        'batch_generation': True,     # 启用批量生成
        'quality_check': True         # 启用质量检查
    }

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'test')
    
    # 测试环境配置
    QUESTION_LANGUAGE = 'english'  # 测试环境使用英文
    AI_QUESTION_CONFIG = {
        **Config.AI_QUESTION_CONFIG,
        'use_mock_ai': True,         # 测试环境使用模拟AI
        'deterministic_output': True  # 确定性输出用于测试
    }

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 