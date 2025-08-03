#!/usr/bin/env python3
"""
Simple Database Initialization Script
不使用SocketIO，只初始化数据库表
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_app():
    """创建简化的Flask应用，不包含SocketIO"""
    app = Flask(__name__)
    
    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'mysql+pymysql://root:rootpassword@mysql:3306/interviewpro'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    return app

def init_database():
    """初始化数据库表"""
    print("🤖 InterviewGenius AI - Simple Database Initialization")
    print("=" * 50)
    
    try:
        # 创建应用
        app = create_simple_app()
        
        # 初始化SQLAlchemy
        db = SQLAlchemy()
        db.init_app(app)
        
        # 导入模型
        with app.app_context():
            from app.models.user import User
            from app.models.resume import Resume
            from app.models.question import Question, Answer, InterviewSession
            from app.models.job import Job
            
            print("🔍 Creating database tables...")
            
            # 创建所有表
            db.create_all()
            
            print("✅ Database tables created successfully!")
            
            # 验证表是否创建成功
            print("🔍 Verifying tables...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users', 'resumes', 'questions', 'answers', 'interview_sessions', 'jobs']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' created")
                else:
                    print(f"❌ Table '{table}' missing")
            
            print(f"📊 Total tables created: {len(tables)}")
            print("🎉 Database initialization completed successfully!")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1) 