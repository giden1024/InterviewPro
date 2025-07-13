#!/usr/bin/env python3
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建最小化的Flask应用
app = Flask(__name__)

# 基本配置
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interview.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# 启用CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化数据库
from app.extensions import db
db.init_app(app)

# 注册简历API蓝图
from app.api.resumes import resumes_bp
app.register_blueprint(resumes_bp, url_prefix='/api/v1/resumes')

@app.route('/health')
def health_check():
    """健康检查"""
    return {
        'status': 'healthy',
        'service': 'interview-genius-minimal'
    }

def create_tables():
    """创建数据库表"""
    with app.app_context():
        db.create_all()
        print("📊 数据库表已创建")

if __name__ == '__main__':
    print("🚀 启动最小化后端服务...")
    print(f"🌐 访问地址: http://localhost:5001")
    
    # 确保上传目录存在
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"📁 创建上传目录: {upload_dir}")
    
    # 创建数据库表
    create_tables()
    
    # 启动应用
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    ) 