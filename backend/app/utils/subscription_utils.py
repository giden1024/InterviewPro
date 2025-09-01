"""
订阅和权限控制工具函数
"""
from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.models.subscription import Subscription
from datetime import datetime
import hashlib
import hmac

def subscription_required(feature: str, usage_type: str = None):
    """
    订阅权限装饰器
    
    Args:
        feature: 功能名称 (voice_interview, custom_questions, advanced_analysis)
        usage_type: 使用类型 (interviews, ai_questions, resume_analysis)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # 获取或创建订阅
            subscription = user.subscription
            if not subscription:
                # 创建免费订阅
                subscription = Subscription(user_id=user_id, plan='free')
                from app.extensions import db
                db.session.add(subscription)
                db.session.commit()
            
            # 检查订阅是否过期
            if subscription.is_expired():
                return jsonify({
                    'error': 'Subscription expired',
                    'message': '您的订阅已过期，请升级订阅以继续使用此功能'
                }), 403
            
            # 检查功能权限
            if feature and not subscription.can_use_feature(feature):
                plan_limits = subscription.get_plan_limits()
                if feature in ['voice_interview', 'custom_questions', 'advanced_analysis']:
                    return jsonify({
                        'error': f'Feature {feature} not available',
                        'message': f'此功能需要升级到更高级的订阅计划',
                        'current_plan': subscription.plan,
                        'required_plans': get_required_plans_for_feature(feature)
                    }), 403
            
            # 检查使用限制
            if usage_type and not subscription.can_use_feature(usage_type):
                limits = subscription.get_plan_limits()
                current_usage = getattr(subscription, f'monthly_{usage_type}_used', 0)
                limit = limits.get(usage_type, 0)
                
                return jsonify({
                    'error': f'Usage limit exceeded',
                    'message': f'本月{get_usage_type_name(usage_type)}使用次数已达上限',
                    'current_usage': current_usage,
                    'limit': limit,
                    'current_plan': subscription.plan,
                    'upgrade_suggestion': get_upgrade_suggestion(subscription.plan)
                }), 403
            
            # 如果有使用类型，增加使用次数
            if usage_type:
                subscription.increment_usage(usage_type)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_required_plans_for_feature(feature: str):
    """获取功能所需的订阅计划"""
    feature_plans = {
        'voice_interview': ['basic', 'premium'],
        'custom_questions': ['premium'],
        'advanced_analysis': ['premium']
    }
    return feature_plans.get(feature, [])

def get_usage_type_name(usage_type: str):
    """获取使用类型的中文名称"""
    names = {
        'interviews': '面试',
        'ai_questions': 'AI问题生成',
        'resume_analysis': '简历分析'
    }
    return names.get(usage_type, usage_type)

def get_upgrade_suggestion(current_plan: str):
    """获取升级建议"""
    suggestions = {
        'free': 'basic',
        'basic': 'premium'
    }
    return suggestions.get(current_plan)

def verify_creem_signature(data: dict, signature: str, api_key: str = None):
    """
    验证Creem.io签名
    
    Args:
        data: 回调数据
        signature: Creem.io提供的签名
        api_key: Creem.io API密钥
    """
    if not api_key:
        api_key = current_app.config.get('CREEM_API_KEY')
    
    if not api_key:
        current_app.logger.error("❌ Creem API key not found")
        return False
    
    current_app.logger.info(f"🔑 Using API key: {api_key[:10]}...{api_key[-4:]}")
    
    # 构建签名字符串 - 按字母顺序排列参数
    sorted_params = sorted(data.items())
    sign_string = '&'.join([f'{key}={value}' for key, value in sorted_params if key != 'signature'])
    
    current_app.logger.info(f"🔐 Sign string: {sign_string}")
    
    # 使用HMAC-SHA256计算签名
    expected_signature = hmac.new(
        api_key.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    current_app.logger.info(f"🔐 Expected signature: {expected_signature}")
    current_app.logger.info(f"🔐 Received signature: {signature}")
    
    # 比较签名
    is_valid = hmac.compare_digest(signature, expected_signature)
    current_app.logger.info(f"🔐 Signature match: {is_valid}")
    
    return is_valid

def get_pricing_plans():
    """获取付费计划配置"""
    return {
        'free': {
            'name': '免费版',
            'price': 0,
            'currency': 'CNY',
            'period': 'month',
            'features': {
                'interviews': 3,
                'ai_questions': 10,
                'resume_analysis': 1,
                'report_history': 7,
                'voice_interview': False,
                'custom_questions': False,
                'advanced_analysis': False
            },
            'description': '适合初次体验用户',
            'highlights': [
                '每月3次面试练习',
                '10个AI生成问题',
                '1次简历分析',
                '7天历史记录'
            ]
        },
        'basic': {
            'name': '基础版',
            'price': 29,
            'currency': 'CNY',
            'period': 'month',
            'features': {
                'interviews': 20,
                'ai_questions': 100,
                'resume_analysis': 5,
                'report_history': 30,
                'voice_interview': True,
                'custom_questions': False,
                'advanced_analysis': False
            },
            'description': '适合求职准备用户',
            'highlights': [
                '每月20次面试练习',
                '100个AI生成问题',
                '5次简历分析',
                '30天历史记录',
                '✅ 语音面试功能'
            ]
        },
        'premium': {
            'name': '高级版',
            'price': 99,
            'currency': 'CNY',
            'period': 'month',
            'features': {
                'interviews': -1,  # 无限
                'ai_questions': -1,
                'resume_analysis': -1,
                'report_history': 365,
                'voice_interview': True,
                'custom_questions': True,
                'advanced_analysis': True
            },
            'description': '适合专业求职者',
            'highlights': [
                '无限次面试练习',
                '无限AI生成问题',
                '无限简历分析',
                '1年历史记录',
                '✅ 语音面试功能',
                '✅ 自定义问题库',
                '✅ 高级分析报告'
            ]
        }
    }

def create_user_subscription(user_id: int, plan: str = 'free'):
    """为用户创建订阅"""
    from app.extensions import db
    
    subscription = Subscription(
        user_id=user_id,
        plan=plan,
        status='active',
        start_date=datetime.utcnow()
    )
    
    if plan != 'free':
        # 付费计划设置30天过期时间
        from datetime import timedelta
        subscription.end_date = datetime.utcnow() + timedelta(days=30)
    
    db.session.add(subscription)
    db.session.commit()
    
    return subscription

def get_user_subscription_status(user_id: int):
    """获取用户订阅状态"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    subscription = user.subscription
    if not subscription:
        # 创建免费订阅
        subscription = create_user_subscription(user_id, 'free')
    
    # 检查是否需要重置月度使用统计
    now = datetime.utcnow()
    if subscription.usage_reset_date.month != now.month or subscription.usage_reset_date.year != now.year:
        subscription.reset_monthly_usage()
    
    limits = subscription.get_plan_limits()
    
    return {
        'subscription': subscription.to_dict(),
        'limits': limits,
        'usage': {
            'interviews': {
                'used': subscription.monthly_interviews_used,
                'limit': limits['interviews'],
                'remaining': limits['interviews'] - subscription.monthly_interviews_used if limits['interviews'] != -1 else -1
            },
            'ai_questions': {
                'used': subscription.monthly_ai_questions_used,
                'limit': limits['ai_questions'],
                'remaining': limits['ai_questions'] - subscription.monthly_ai_questions_used if limits['ai_questions'] != -1 else -1
            },
            'resume_analysis': {
                'used': subscription.monthly_resume_analysis_used,
                'limit': limits['resume_analysis'],
                'remaining': limits['resume_analysis'] - subscription.monthly_resume_analysis_used if limits['resume_analysis'] != -1 else -1
            }
        },
        'features': {
            'voice_interview': limits['voice_interview'],
            'custom_questions': limits['custom_questions'],
            'advanced_analysis': limits['advanced_analysis']
        },
        'is_expired': subscription.is_expired()
    }
