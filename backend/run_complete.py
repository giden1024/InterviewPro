#!/usr/bin/env python3
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 根据环境变量加载配置类
import os
from app.config import DevelopmentConfig, ProductionConfig

# 根据环境变量决定使用哪个配置
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# 补充JWT配置
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# 启用CORS - 修复配置以支持所有端点
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", 
                   "http://localhost:3003", "http://localhost:3004", "http://localhost:3005", 
                   "http://localhost:3006", "http://localhost:3007"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 初始化数据库和扩展
from app.extensions import db, jwt, init_redis
db.init_app(app)
jwt.init_app(app)

# 初始化Redis
init_redis(app)

# 注册所有API蓝图
from app.api.auth import auth_bp
from app.api.resumes import resumes_bp
from app.api.interviews import interviews_bp
from app.api.questions import questions_bp
from app.api.analysis import analysis
from app.api.jobs import jobs_bp

app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(resumes_bp, url_prefix='/api/v1/resumes')
app.register_blueprint(interviews_bp, url_prefix='/api/v1/interviews')
app.register_blueprint(questions_bp, url_prefix='/api/v1/questions')
app.register_blueprint(analysis, url_prefix='/api/v1/analysis')
app.register_blueprint(jobs_bp, url_prefix='/api/v1/jobs')

# 注册异常处理器
from app.utils.exceptions import handle_errors
handle_errors(app)

# 开发用的测试API
@app.route('/api/v1/dev/create-test-user', methods=['POST'])
def create_test_user():
    """创建测试用户"""
    try:
        from app.models.user import User
        from flask_jwt_extended import create_access_token
        
        # 检查是否已存在
        existing_user = User.query.filter_by(email='test@example.com').first()
        if existing_user:
            access_token = create_access_token(identity=str(existing_user.id))
            return jsonify({
                'success': True,
                'message': '测试用户已存在',
                'data': {
                    'access_token': access_token,
                    'user': existing_user.to_dict()
                }
            })
        
        # 创建测试用户
        user = User(
            email='test@example.com',
            username='测试用户'
        )
        user.set_password('123456')
        
        db.session.add(user)
        db.session.commit()
        
        # 生成token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': '测试用户创建成功',
            'data': {
                'access_token': access_token,
                'user': user.to_dict()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建测试用户失败: {str(e)}'
        }), 500

@app.route('/api/v1/dev/login', methods=['POST'])
def dev_login():
    """开发用快速登录"""
    try:
        from app.models.user import User
        from flask_jwt_extended import create_access_token
        from flask import request
        
        # 获取请求数据
        data = request.get_json() or {}
        email = data.get('email', 'test@example.com')
        password = data.get('password', '123456')
        
        # 查找或创建用户
        user = User.query.filter_by(email=email).first()
        if not user:
            # 创建新用户
            username = email.split('@')[0]  # 使用邮箱前缀作为用户名
            user = User(
                email=email,
                username=username
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"✅ 创建新用户: {email}")
        
        # 生成token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': access_token,
                'user': user.to_dict()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@app.route('/api/v1/dev/fix-resume-owner', methods=['POST'])
def fix_resume_owner():
    """开发用：修复简历所有者"""
    try:
        from app.models.resume import Resume
        from flask import request
        
        data = request.get_json() or {}
        resume_id = data.get('resume_id', 1)
        new_user_id = data.get('user_id', 2)
        
        # 查找简历
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({
                'success': False,
                'message': f'简历 {resume_id} 不存在'
            }), 404
        
        # 更新所有者
        old_user_id = resume.user_id
        resume.user_id = new_user_id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'简历 {resume_id} 所有者已从用户 {old_user_id} 更改为用户 {new_user_id}',
            'data': {
                'resume_id': resume_id,
                'old_user_id': old_user_id,
                'new_user_id': new_user_id
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'修复失败: {str(e)}'
        }), 500

@app.route('/')
def index():
    """主页"""
    return {
        'success': True,
        'message': 'InterviewGenius AI 后端服务运行正常',
        'version': '1.0.0'
    }

@app.route('/health')
def health_check():
    """健康检查"""
    return {
        'service': 'interview-genius-complete',
        'status': 'healthy'
    }

@app.route('/api/v1/analysis/test-direct', methods=['GET'])
def test_analysis_direct():
    """直接测试分析路由"""
    print("🔍 [DEBUG] 直接分析测试路由被调用!")
    return jsonify({
        'success': True,
        'message': '直接分析测试路由工作正常',
        'data': {'test': True}
    })

def create_tables():
    """创建数据库表"""
    with app.app_context():
        db.create_all()
        print("📊 数据库表已创建")

if __name__ == '__main__':
    print("🚀 启动完整后端服务...")
    print(f"🌐 访问地址: http://localhost:5001")
    print("📋 可用API:")
    print("  - /api/v1/auth/*")
    print("  - /api/v1/resumes/*")
    print("  - /api/v1/interviews/*")
    print("  - /api/v1/questions/*")
    print("  - /api/v1/analysis/*")
    print("  - /api/v1/jobs/*")
    print("🔧 开发API:")
    print("  - POST /api/v1/dev/create-test-user")
    print("  - POST /api/v1/dev/login")
    
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
        debug=False,  # 关闭调试模式避免重载问题
        threaded=True,
        use_reloader=False  # 禁用重载器
    ) 