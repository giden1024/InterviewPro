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
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    redis_client = redis.from_url(redis_url, decode_responses=True) 