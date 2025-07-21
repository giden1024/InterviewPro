from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError as MarshmallowValidationError, validates, validates_schema

from app.models.user import User
from app.extensions import db
from app.utils.exceptions import APIError, ValidationError, AuthenticationError

auth_bp = Blueprint('auth', __name__)

# 自定义密码验证函数
def validate_password_length(value):
    if len(value) < 6:
        raise MarshmallowValidationError('Password must be at least 6 characters')

# 验证模式
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate_password_length)
    username = fields.Str(allow_none=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        # 数据验证
        schema = RegisterSchema()
        data = schema.load(request.get_json() or {})
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            raise ValidationError("Email is already registered")
        
        # 创建新用户
        user = User(
            email=data['email'],
            username=data.get('username')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # 生成令牌
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        }), 201
        
    except MarshmallowValidationError as e:
        raise APIError('Data validation failed', 422, e.messages)
    except (ValidationError, AuthenticationError, APIError):
        raise  # 直接重新抛出我们的自定义异常
    except Exception as e:
        raise APIError(str(e), 400)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 数据验证
        schema = LoginSchema()
        data = schema.load(request.get_json() or {})
        
        # 首先检查用户是否存在
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            raise AuthenticationError("User does not exist, please check your email address")
        
        # 检查用户是否激活
        if not user.is_active:
            raise AuthenticationError("User account has been disabled")
        
        # 验证密码
        if not user.check_password(data['password']):
            raise AuthenticationError("Incorrect password, please try again")
        
        # 更新最后登录时间
        user.update_last_login()
        
        # 生成令牌
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        })
        
    except MarshmallowValidationError as e:
        raise APIError('Data validation failed', 422, e.messages)
    except (ValidationError, AuthenticationError, APIError):
        raise  # 直接重新抛出我们的自定义异常
    except Exception as e:
        raise APIError(str(e), 400)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            raise ValidationError("User does not exist")
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
        
    except Exception as e:
        raise APIError(str(e), 400)

@auth_bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取用户信息 (前端兼容接口)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            raise ValidationError("User does not exist")
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
        
    except Exception as e:
        raise APIError(str(e), 400)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    # TODO: 实现令牌黑名单
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }) 