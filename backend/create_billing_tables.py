#!/usr/bin/env python3
"""
创建付费模块相关数据表的脚本
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.subscription import Subscription, PaymentHistory
from app.models.user import User

def create_billing_tables():
    """创建付费相关数据表"""
    print("🚀 开始创建付费模块数据表...")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            # 创建表
            print("📋 创建订阅表 (subscriptions)...")
            db.create_all()
            
            print("✅ 数据表创建成功！")
            
            # 检查表是否创建成功
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n📊 当前数据库表列表:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            # 验证付费相关表
            billing_tables = ['subscriptions', 'payment_history']
            missing_tables = [table for table in billing_tables if table not in tables]
            
            if missing_tables:
                print(f"\n⚠️  警告: 以下表未创建成功: {', '.join(missing_tables)}")
                return False
            else:
                print(f"\n✅ 付费模块表创建成功: {', '.join(billing_tables)}")
            
            # 为现有用户创建免费订阅
            print("\n👥 为现有用户创建免费订阅...")
            users_without_subscription = User.query.outerjoin(Subscription).filter(Subscription.id == None).all()
            
            created_count = 0
            for user in users_without_subscription:
                subscription = Subscription(
                    user_id=user.id,
                    plan='free',
                    status='active',
                    start_date=datetime.utcnow()
                )
                db.session.add(subscription)
                created_count += 1
            
            if created_count > 0:
                db.session.commit()
                print(f"✅ 为 {created_count} 个用户创建了免费订阅")
            else:
                print("ℹ️  所有用户都已有订阅记录")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建数据表失败: {str(e)}")
            db.session.rollback()
            return False

def check_billing_setup():
    """检查付费模块设置"""
    print("\n🔍 检查付费模块配置...")
    
    app = create_app()
    
    with app.app_context():
        # 检查配置
        config_items = [
            ('CREEM_API_KEY', app.config.get('CREEM_API_KEY')),
            ('CREEM_TEST_MODE', app.config.get('CREEM_TEST_MODE')),
            ('CREEM_TEST_PRODUCT_ID', app.config.get('CREEM_TEST_PRODUCT_ID')),
            ('FRONTEND_URL', app.config.get('FRONTEND_URL'))
        ]
        
        print("📋 配置检查:")
        for key, value in config_items:
            status = "✅" if value else "❌"
            masked_value = value[:10] + "..." if value and len(str(value)) > 10 else value
            print(f"  {status} {key}: {masked_value}")
        
        # 检查数据库连接
        try:
            db.session.execute(db.text('SELECT 1'))
            print("✅ 数据库连接正常")
        except Exception as e:
            print(f"❌ 数据库连接失败: {str(e)}")
        
        # 检查表结构
        inspector = db.inspect(db.engine)
        
        # 检查subscriptions表结构
        if 'subscriptions' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('subscriptions')]
            expected_columns = [
                'id', 'user_id', 'plan', 'status', 'creem_customer_id', 
                'creem_subscription_id', 'creem_order_id', 'start_date', 
                'end_date', 'monthly_interviews_used', 'monthly_ai_questions_used',
                'monthly_resume_analysis_used', 'created_at', 'updated_at'
            ]
            
            missing_columns = [col for col in expected_columns if col not in columns]
            if missing_columns:
                print(f"⚠️  subscriptions表缺少列: {', '.join(missing_columns)}")
            else:
                print("✅ subscriptions表结构正确")
        
        # 检查payment_history表结构
        if 'payment_history' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('payment_history')]
            expected_columns = [
                'id', 'user_id', 'subscription_id', 'creem_checkout_id',
                'creem_order_id', 'creem_customer_id', 'request_id', 'plan',
                'amount', 'currency', 'status', 'payment_date', 'created_at'
            ]
            
            missing_columns = [col for col in expected_columns if col not in columns]
            if missing_columns:
                print(f"⚠️  payment_history表缺少列: {', '.join(missing_columns)}")
            else:
                print("✅ payment_history表结构正确")

def test_billing_api():
    """测试付费API端点"""
    print("\n🧪 测试付费API端点...")
    
    app = create_app()
    
    with app.test_client() as client:
        # 测试获取付费计划
        response = client.get('/api/v1/billing/plans')
        if response.status_code == 200:
            print("✅ GET /api/v1/billing/plans - 正常")
        else:
            print(f"❌ GET /api/v1/billing/plans - 失败 ({response.status_code})")
        
        # 测试其他端点（需要认证）
        endpoints = [
            '/api/v1/billing/subscription',
            '/api/v1/billing/usage',
            '/api/v1/billing/history'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            if response.status_code == 401:  # 未认证是预期的
                print(f"✅ GET {endpoint} - 需要认证 (预期)")
            elif response.status_code == 422:  # JWT错误也是预期的
                print(f"✅ GET {endpoint} - JWT错误 (预期)")
            else:
                print(f"⚠️  GET {endpoint} - 状态码: {response.status_code}")

def main():
    """主函数"""
    print("🎯 InterviewPro 付费模块初始化")
    print("=" * 50)
    
    # 创建数据表
    if not create_billing_tables():
        print("\n❌ 数据表创建失败，请检查错误信息")
        sys.exit(1)
    
    # 检查配置
    check_billing_setup()
    
    # 测试API
    test_billing_api()
    
    print("\n" + "=" * 50)
    print("🎉 付费模块初始化完成！")
    print("\n📋 下一步操作:")
    print("1. 启动后端服务: python run_complete.py")
    print("2. 启动前端服务: cd frontend && npm run dev") 
    print("3. 访问付费页面测试功能")
    print("4. 在Creem.io测试模式下进行支付测试")
    
    print("\n🔗 相关链接:")
    print("- 后端API: http://localhost:5001/api/v1/billing/plans")
    print("- 前端页面: http://localhost:3000/billing")
    print("- Creem.io文档: https://docs.creem.io/checkout-flow")

if __name__ == '__main__':
    main()
