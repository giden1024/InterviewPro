#!/usr/bin/env python3
"""
演示如何在现有API中使用订阅权限控制
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.subscription_utils import subscription_required

# 创建演示蓝图
demo_bp = Blueprint('demo', __name__)

@demo_bp.route('/basic-interview', methods=['POST'])
@jwt_required()
@subscription_required('interviews', 'interviews')  # 需要面试功能，消耗面试次数
def start_basic_interview():
    """开始基础面试 - 需要消耗面试次数"""
    user_id = get_jwt_identity()
    
    # 这里实现面试逻辑
    # 由于使用了 @subscription_required 装饰器，
    # 已经自动检查了用户权限并扣除了使用次数
    
    return jsonify({
        'success': True,
        'message': '面试开始成功',
        'interview_id': 'demo_interview_123'
    })

@demo_bp.route('/voice-interview', methods=['POST'])
@jwt_required()
@subscription_required('voice_interview')  # 需要语音面试功能
def start_voice_interview():
    """开始语音面试 - 需要高级功能权限"""
    user_id = get_jwt_identity()
    
    return jsonify({
        'success': True,
        'message': '语音面试开始成功',
        'interview_id': 'voice_interview_123'
    })

@demo_bp.route('/generate-questions', methods=['POST'])
@jwt_required()
@subscription_required('ai_questions', 'ai_questions')  # 消耗AI问题生成次数
def generate_ai_questions():
    """生成AI问题 - 消耗AI问题次数"""
    user_id = get_jwt_identity()
    
    return jsonify({
        'success': True,
        'questions': [
            '请介绍一下您的工作经验',
            '您如何处理工作中的压力？',
            '描述一次您解决困难问题的经历'
        ]
    })

@demo_bp.route('/analyze-resume', methods=['POST'])
@jwt_required()
@subscription_required('resume_analysis', 'resume_analysis')  # 消耗简历分析次数
def analyze_resume():
    """分析简历 - 消耗简历分析次数"""
    user_id = get_jwt_identity()
    
    return jsonify({
        'success': True,
        'analysis': {
            'score': 85,
            'strengths': ['丰富的工作经验', '技能匹配度高'],
            'suggestions': ['增加项目经验描述', '完善教育背景']
        }
    })

@demo_bp.route('/advanced-report', methods=['GET'])
@jwt_required()
@subscription_required('advanced_analysis')  # 需要高级分析功能
def get_advanced_report():
    """获取高级分析报告 - 需要高级功能权限"""
    user_id = get_jwt_identity()
    
    return jsonify({
        'success': True,
        'report': {
            'overall_score': 88,
            'detailed_analysis': '详细的面试表现分析...',
            'improvement_plan': '个性化改进建议...',
            'industry_comparison': '行业对比数据...'
        }
    })

def demo_usage_examples():
    """演示如何使用订阅功能"""
    print("🎯 订阅功能使用示例")
    print("=" * 50)
    
    print("\n📋 1. 基础使用模式:")
    print("""
@demo_bp.route('/your-endpoint', methods=['POST'])
@jwt_required()
@subscription_required('feature_name', 'usage_type')
def your_function():
    # 功能实现
    return jsonify({'success': True})
    """)
    
    print("\n📋 2. 功能权限检查:")
    print("- voice_interview: 语音面试功能")
    print("- custom_questions: 自定义问题功能") 
    print("- advanced_analysis: 高级分析功能")
    
    print("\n📋 3. 使用次数控制:")
    print("- interviews: 面试次数")
    print("- ai_questions: AI问题生成次数")
    print("- resume_analysis: 简历分析次数")
    
    print("\n📋 4. 错误处理:")
    print("当用户权限不足时，装饰器会自动返回:")
    print("""
{
    "error": "Feature not available",
    "message": "此功能需要升级到更高级的订阅计划",
    "current_plan": "free",
    "required_plans": ["basic", "premium"]
}
""")
    
    print("\n📋 5. 使用限制超出时:")
    print("""
{
    "error": "Usage limit exceeded", 
    "message": "本月面试使用次数已达上限",
    "current_usage": 3,
    "limit": 3,
    "current_plan": "free",
    "upgrade_suggestion": "basic"
}
""")

def integration_checklist():
    """集成检查清单"""
    print("\n✅ 集成检查清单:")
    print("=" * 30)
    
    checklist = [
        ("数据库表创建", "运行 create_billing_tables.py"),
        ("API蓝图注册", "在 app/__init__.py 中注册 billing_bp"),
        ("环境变量配置", "设置 CREEM_API_KEY 等配置"),
        ("前端服务创建", "创建 billingService.ts"),
        ("付费页面创建", "创建 BillingPage.tsx"),
        ("权限装饰器使用", "在需要的API端点添加 @subscription_required"),
        ("支付回调处理", "配置 /api/v1/billing/callback 路由"),
        ("测试支付流程", "使用测试API密钥进行支付测试")
    ]
    
    for i, (item, description) in enumerate(checklist, 1):
        print(f"{i:2d}. ✅ {item}")
        print(f"     {description}")

if __name__ == '__main__':
    demo_usage_examples()
    integration_checklist()
    
    print("\n🎉 付费模块集成完成！")
    print("\n🚀 启动测试:")
    print("1. 运行: ./start_billing_test.sh")
    print("2. 或手动启动: python run_complete.py")
    print("3. 测试API: http://localhost:5001/api/v1/billing/plans")
