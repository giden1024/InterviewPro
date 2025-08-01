from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# 数据库
db = SQLAlchemy()
migrate = Migrate()

# 认证
jwt = JWTManager()

# 跨域
cors = CORS()

# WebSocket
socketio = SocketIO()

# 限流
limiter = Limiter(key_func=get_remote_address)

# Redis客户端
redis_client = None

def init_redis(app):
    """初始化Redis客户端"""
    global redis_client
    try:
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        client = redis.from_url(redis_url, decode_responses=True)
        
        # 测试连接
        client.ping()
        print(f"✅ Redis连接成功: {redis_url}")
        
        # 只有在连接成功后才赋值给全局变量
        redis_client = client
        
        # 同时存储到app配置中，以便在应用上下文中访问
        app.config['REDIS_CLIENT'] = client
        return True
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        redis_client = None
        return False

def get_redis_client():
    """获取Redis客户端，优先从current_app获取"""
    from flask import current_app
    try:
        # 首先尝试从current_app获取
        if current_app and hasattr(current_app, 'config'):
            return current_app.config.get('REDIS_CLIENT')
    except:
        pass
    
    # 如果current_app不可用，返回全局变量
    return redis_client 