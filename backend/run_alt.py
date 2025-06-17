#!/usr/bin/env python3
import os
from app import create_app
from app.extensions import db, socketio

# 创建应用实例
app = create_app()

@app.route('/')
def index():
    """健康检查端点"""
    return {
        'success': True,
        'message': 'InterviewGenius AI 后端服务运行正常',
        'version': '1.0.0'
    }

@app.route('/health')
def health_check():
    """健康检查"""
    return {
        'status': 'healthy',
        'service': 'interview-genius-backend'
    }

def create_tables():
    """创建数据库表"""
    with app.app_context():
        db.create_all()
        print("数据库表已创建")

if __name__ == '__main__':
    # 开发环境运行配置
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 启动 InterviewGenius AI 后端服务...")
    print(f"📊 调试模式: {'开启' if debug_mode else '关闭'}")
    print(f"🌐 访问地址: http://localhost:5001")
    
    # 创建数据库表
    create_tables()
    
    # 使用SocketIO运行应用 - 使用5001端口避免冲突
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=debug_mode,
        allow_unsafe_werkzeug=True  # 开发环境允许
    ) 