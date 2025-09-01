#!/usr/bin/env python3
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)

    # 根据环境变量决定使用哪个配置
    config_name = os.environ.get('FLASK_ENV', 'development')
    if config_name == 'production':
        from app.config import ProductionConfig
        app.config.from_object(ProductionConfig)
        print(f"🔧 使用生产环境配置")
    else:
        from app.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
        print(f"🔧 使用开发环境配置")

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

    # 初始化数据库和扩展 - 在应用配置完成后
    from app.extensions import db, jwt
    db.init_app(app)
    jwt.init_app(app)
    
    print(f"🗄️ 数据库URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # 在应用上下文中导入模型
    with app.app_context():
        # 导入所有模型以确保表定义被注册
        from app.models.user import User
        from app.models.resume import Resume
        from app.models.question import Question, InterviewSession
        
        # 创建表
        db.create_all()
        print("📊 数据库表已创建/更新")

    # 注册所有API蓝图 - 修复analysis导入
    from app.api.auth import auth_bp
    from app.api.resumes import resumes_bp
    from app.api.interviews import interviews_bp
    from app.api.questions import questions_bp
    from app.api.analysis import analysis  # 修复：导入analysis而不是analysis_bp
    from app.api.jobs import jobs_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(resumes_bp, url_prefix='/api/v1/resumes')
    app.register_blueprint(interviews_bp, url_prefix='/api/v1/interviews')
    app.register_blueprint(questions_bp, url_prefix='/api/v1/questions')
    app.register_blueprint(analysis, url_prefix='/api/v1/analysis')  # 修复：使用analysis
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
            print(f"❌ 登录错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'登录失败: {str(e)}'
            }), 500

    @app.route('/')
    def index():
        """主页"""
        return {
            'success': True,
            'message': 'InterviewGenius AI 后端服务运行正常',
            'version': '1.0.0',
            'database': app.config.get('SQLALCHEMY_DATABASE_URI', '未配置')[:50] + '...'
        }

    @app.route('/health')
    def health_check():
        """健康检查"""
        return {
            'service': 'interview-genius-complete',
            'status': 'healthy',
            'database_configured': 'mysql' in app.config.get('SQLALCHEMY_DATABASE_URI', '').lower()
        }

    @app.route('/api/v1/health')
    def api_health_check():
        """API健康检查 - 用于Docker healthcheck"""
        return {
            'service': 'interview-genius-complete',
            'status': 'healthy',
            'version': '1.0.0',
            'database_configured': 'mysql' in app.config.get('SQLALCHEMY_DATABASE_URI', '').lower()
        }

    return app

# 为Gunicorn创建应用实例
app = create_app()

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
    upload_dir = app.config.get('UPLOAD_FOLDER', '/app/uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"📁 创建上传目录: {upload_dir}")
    
    # 启动应用
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False,  # 关闭调试模式避免重载问题
        threaded=True,
        use_reloader=False  # 禁用重载器
    ) 