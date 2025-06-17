from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError as MarshmallowValidationError

from app.models.user import User
from app.extensions import db
from app.utils.exceptions import APIError, ValidationError, AuthenticationError

auth_bp = Blueprint('auth', __name__)

# 验证模式
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)
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
            raise ValidationError("邮箱已被注册")
        
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
            'message': '注册成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        }), 201
        
    except MarshmallowValidationError as e:
        raise APIError('数据验证失败', 422, e.messages)
    except Exception as e:
        raise APIError(str(e), 400)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 数据验证
        schema = LoginSchema()
        data = schema.load(request.get_json() or {})
        
        # 验证用户
        user = User.query.filter_by(email=data['email'], is_active=True).first()
        
        if not user or not user.check_password(data['password']):
            raise AuthenticationError("邮箱或密码错误")
        
        # 更新最后登录时间
        user.update_last_login()
        
        # 生成令牌
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        })
        
    except MarshmallowValidationError as e:
        raise APIError('数据验证失败', 422, e.messages)
    except (AuthenticationError, APIError):
        raise
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
            raise ValidationError("用户不存在")
        
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
            raise ValidationError("用户不存在")
        
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
        'message': '登出成功'
    }) 