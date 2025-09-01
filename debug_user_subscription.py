#!/usr/bin/env python3
"""
调试用户订阅状态
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.app.models.user import User
from backend.app.models.subscription import Subscription, PaymentHistory
from backend.app.utils.subscription_utils import get_user_subscription_status
from datetime import datetime

def debug_user_subscription(email):
    """调试指定用户的订阅状态"""
    app = create_app()
    with app.app_context():
        print(f"🔍 调试用户订阅状态: {email}")
        print("=" * 60)
        
        # 1. 查找用户
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ 用户不存在: {email}")
            return
        
        print(f"✅ 找到用户:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   创建时间: {user.created_at}")
        print(f"   最后登录: {user.last_login_at}")
        print()
        
        # 2. 查看订阅信息
        subscription = user.subscription
        if not subscription:
            print("❌ 用户没有订阅记录")
            return
        
        print(f"📋 订阅信息:")
        print(f"   计划: {subscription.plan}")
        print(f"   状态: {subscription.status}")
        print(f"   开始时间: {subscription.start_date}")
        print(f"   结束时间: {subscription.end_date}")
        print(f"   是否过期: {subscription.is_expired()}")
        print()
        
        # 3. 查看使用统计
        print(f"📊 使用统计:")
        print(f"   面试使用: {subscription.monthly_interviews_used}")
        print(f"   AI问题使用: {subscription.monthly_ai_questions_used}")
        print(f"   简历分析使用: {subscription.monthly_resume_analysis_used}")
        print(f"   统计重置日期: {subscription.usage_reset_date}")
        print()
        
        # 4. 获取计划限制
        limits = subscription.get_plan_limits()
        print(f"🎯 计划限制:")
        for key, value in limits.items():
            print(f"   {key}: {value}")
        print()
        
        # 5. 查看支付历史
        payments = PaymentHistory.query.filter_by(user_id=user.id).order_by(PaymentHistory.created_at.desc()).all()
        print(f"💳 支付历史 ({len(payments)} 条记录):")
        if payments:
            for payment in payments:
                print(f"   ID: {payment.id}")
                print(f"   计划: {payment.plan}")
                print(f"   金额: ¥{payment.amount}")
                print(f"   状态: {payment.status}")
                print(f"   支付时间: {payment.payment_date}")
                print(f"   创建时间: {payment.created_at}")
                print(f"   Request ID: {payment.request_id}")
                print(f"   Checkout ID: {payment.creem_checkout_id}")
                print(f"   ---")
        else:
            print("   无支付记录")
        print()
        
        # 6. 使用工具函数获取状态
        subscription_status = get_user_subscription_status(user.id)
        if subscription_status:
            print(f"🔧 通过工具函数获取的状态:")
            print(f"   计划: {subscription_status['subscription']['plan']}")
            print(f"   面试使用: {subscription_status['usage']['interviews']['used']}/{subscription_status['usage']['interviews']['limit']}")
            print(f"   AI问题使用: {subscription_status['usage']['ai_questions']['used']}/{subscription_status['usage']['ai_questions']['limit']}")
            print(f"   简历分析使用: {subscription_status['usage']['resume_analysis']['used']}/{subscription_status['usage']['resume_analysis']['limit']}")
            print(f"   功能权限:")
            for feature, enabled in subscription_status['features'].items():
                print(f"     {feature}: {'✅' if enabled else '❌'}")
        
        # 7. 诊断建议
        print(f"\n🎯 诊断结果:")
        if subscription.plan == 'free':
            if payments:
                completed_payments = [p for p in payments if p.status == 'completed']
                if completed_payments:
                    print("⚠️  发现已完成的支付记录，但订阅计划仍为免费版")
                    print("   可能原因：支付回调处理失败")
                    latest_payment = completed_payments[0]
                    print(f"   建议：手动更新订阅到 {latest_payment.plan} 计划")
                else:
                    print("ℹ️  所有支付都未完成，订阅保持免费版是正常的")
            else:
                print("ℹ️  没有支付记录，显示免费版是正常的")
        else:
            print(f"✅ 订阅计划正确: {subscription.plan}")
            if subscription.is_expired():
                print("⚠️  但订阅已过期")

def manual_upgrade_user(email, plan):
    """手动升级用户订阅"""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ 用户不存在: {email}")
            return
        
        subscription = user.subscription
        if not subscription:
            print("❌ 用户没有订阅记录")
            return
        
        print(f"🔧 手动升级用户 {email} 到 {plan} 计划...")
        
        # 更新订阅
        subscription.plan = plan
        subscription.status = 'active'
        subscription.start_date = datetime.utcnow()
        if plan != 'free':
            from datetime import timedelta
            subscription.end_date = datetime.utcnow() + timedelta(days=30)
        
        # 重置使用统计
        subscription.monthly_interviews_used = 0
        subscription.monthly_ai_questions_used = 0
        subscription.monthly_resume_analysis_used = 0
        subscription.usage_reset_date = datetime.utcnow().replace(day=1)
        
        from backend.app.extensions import db
        db.session.commit()
        
        print(f"✅ 升级完成！用户现在是 {plan} 计划")

if __name__ == "__main__":
    email = "393893095@qq.com"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "upgrade" and len(sys.argv) > 2:
            plan = sys.argv[2]
            manual_upgrade_user(email, plan)
        else:
            email = sys.argv[1]
    
    debug_user_subscription(email)
