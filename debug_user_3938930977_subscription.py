#!/usr/bin/env python3
"""
诊断用户3938930977@qq.com的订阅和支付状态
"""
import sys
import os
sys.path.append('/Users/mayuyang/InterviewPro/backend')

from app import create_app
from app.models.subscription import Subscription, PaymentHistory
from app.models.user import User
from sqlalchemy import desc
from datetime import datetime

def main():
    app = create_app()
    
    with app.app_context():
        print("🔍 查询用户: 3938930977@qq.com")
        print("=" * 60)
        
        # 查找用户
        user = User.query.filter_by(email='3938930977@qq.com').first()
        if not user:
            print("❌ 用户不存在")
            return
        
        print(f"✅ 用户ID: {user.id}")
        print(f"📧 邮箱: {user.email}")
        print(f"👤 用户名: {user.username}")
        print()
        
        # 查询订阅状态
        subscription = Subscription.query.filter_by(user_id=user.id).first()
        if subscription:
            print("📋 当前订阅状态:")
            print(f"  - 计划: {subscription.plan}")
            print(f"  - 状态: {subscription.status}")
            print(f"  - 开始日期: {subscription.start_date}")
            print(f"  - 结束日期: {subscription.end_date}")
            print(f"  - 本月面试使用: {subscription.monthly_interviews_used}")
            print(f"  - 本月AI问题使用: {subscription.monthly_ai_questions_used}")
            print(f"  - 本月简历分析使用: {subscription.monthly_resume_analysis_used}")
            print(f"  - 使用重置日期: {subscription.usage_reset_date}")
        else:
            print("❌ 未找到订阅记录")
        print()
        
        # 查询支付历史（最近5条）
        payments = PaymentHistory.query.filter_by(user_id=user.id).order_by(desc(PaymentHistory.created_at)).limit(5).all()
        if payments:
            print("💳 最近5条支付记录:")
            for i, payment in enumerate(payments, 1):
                print(f"  {i}. Request ID: {payment.request_id}")
                print(f"     - 计划: {payment.plan}")
                print(f"     - 金额: ¥{payment.amount}")
                print(f"     - 状态: {payment.status}")
                print(f"     - Checkout ID: {payment.creem_checkout_id}")
                print(f"     - 创建时间: {payment.created_at}")
                # print(f"     - 更新时间: {payment.updated_at}")
                print()
        else:
            print("❌ 未找到支付记录")

if __name__ == '__main__':
    main()
