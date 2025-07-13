import os
from flask import Flask
from dotenv import load_dotenv

from app.config import config
from app.extensions import db, migrate, jwt, cors, socketio, limiter, init_redis

# 加载环境变量
load_dotenv()

def create_app(config_name=None):
    """Flask应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # CORS配置已在run_complete.py中处理
    # cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    # 优化SocketIO配置
    socketio.init_app(
        app, 
        cors_allowed_origins="*", 
        async_mode='gevent',
        logger=True,
        engineio_logger=True
    )
    
    limiter.init_app(app)
    init_redis(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册WebSocket事件
    register_socket_events()
    
    return app

def register_blueprints(app):
    """注册蓝图"""
    # 延迟导入避免循环依赖
    from app.api.auth import auth_bp
    from app.api.resumes import resumes_bp
    from app.api.interviews import interviews_bp
    from app.api.questions import questions_bp
    from app.api.analysis import analysis
    from app.api.jobs import jobs_bp
    from app.api.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(resumes_bp, url_prefix='/api/v1/resumes')
    app.register_blueprint(interviews_bp, url_prefix='/api/v1/interviews')
    app.register_blueprint(questions_bp, url_prefix='/api/v1/questions')
    app.register_blueprint(analysis, url_prefix='/api/v1/analysis')
    app.register_blueprint(jobs_bp, url_prefix='/api/v1/jobs')
    app.register_blueprint(health_bp, url_prefix='/api/v1')

def register_error_handlers(app):
    """注册错误处理器"""
    from app.utils.exceptions import handle_errors
    handle_errors(app)

def register_socket_events():
    """注册WebSocket事件"""
    from app.websocket.handlers import register_socket_events
    register_socket_events(socketio)
