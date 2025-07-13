#!/usr/bin/env python3
"""
调试版本的后端启动脚本
禁用SocketIO以便排查问题
"""

import os
import sys
from flask import Flask
from flask_cors import CORS

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import config
from app.extensions import db, migrate, jwt
from app.models import User, Resume, InterviewSession, Question, Answer, Job

def create_debug_app():
    """创建调试版本的Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    
    # 初始化基础扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 配置CORS
    CORS(app, 
         origins=["http://localhost:3000", "http://localhost:3001"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # 注册蓝图
    register_blueprints(app)
    
    # 确保数据库表存在
    with app.app_context():
        try:
            db.create_all()
            print("📊 数据库表已创建")
        except Exception as e:
            print(f"❌ 数据库创建失败: {e}")
    
    return app

def register_blueprints(app):
    """注册蓝图"""
    try:
        from app.api.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        print("✅ Auth蓝图已注册")
    except Exception as e:
        print(f"❌ Auth蓝图注册失败: {e}")
    
    try:
        from app.api.resumes import resumes_bp
        app.register_blueprint(resumes_bp, url_prefix='/api/v1/resumes')
        print("✅ Resumes蓝图已注册")
    except Exception as e:
        print(f"❌ Resumes蓝图注册失败: {e}")
    
    try:
        from app.api.interviews import interviews_bp
        app.register_blueprint(interviews_bp, url_prefix='/api/v1/interviews')
        print("✅ Interviews蓝图已注册")
    except Exception as e:
        print(f"❌ Interviews蓝图注册失败: {e}")
    
    try:
        from app.api.questions import questions_bp
        app.register_blueprint(questions_bp, url_prefix='/api/v1/questions')
        print("✅ Questions蓝图已注册")
    except Exception as e:
        print(f"❌ Questions蓝图注册失败: {e}")
    
    try:
        from app.api.analysis import analysis
        app.register_blueprint(analysis, url_prefix='/api/v1/analysis')
        print("✅ Analysis蓝图已注册")
    except Exception as e:
        print(f"❌ Analysis蓝图注册失败: {e}")
    
    try:
        from app.api.jobs import jobs_bp
        app.register_blueprint(jobs_bp, url_prefix='/api/v1/jobs')
        print("✅ Jobs蓝图已注册")
    except Exception as e:
        print(f"❌ Jobs蓝图注册失败: {e}")
    
    try:
        from app.api.health import health_bp
        app.register_blueprint(health_bp, url_prefix='/api/v1')
        print("✅ Health蓝图已注册")
    except Exception as e:
        print(f"❌ Health蓝图注册失败: {e}")

if __name__ == "__main__":
    print("🚀 启动调试版本后端服务...")
    print("🌐 访问地址: http://localhost:5001")
    
    app = create_debug_app()
    
    try:
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            threaded=True
        )
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1) 