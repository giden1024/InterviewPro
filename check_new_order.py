#!/usr/bin/env python3
"""
检查指定订单的详细状态
"""
import sys
import os
sys.path.append('/Users/mayuyang/InterviewPro/backend')

from app import create_app
from app.models.subscription import Subscription, PaymentHistory
from app.models.user import User
from sqlalchemy import desc
from datetime import datetime, timedelta

def check_order(request_id):
    app = create_app()
    
    with app.app_context():
        print(f"🔍 检查订单: {request_id}")
        print("=" * 60)
        
        # 查找支付记录
        payment = PaymentHistory.query.filter_by(request_id=request_id).first()
        if not payment:
            print("❌ 未找到支付记录")
            return
        
        print("💳 支付记录详情:")
        print(f"  - Request ID: {payment.request_id}")
        print(f"  - 用户ID: {payment.user_id}")
        print(f"  - 计划: {payment.plan}")
        print(f"  - 金额: ¥{payment.amount}")
        print(f"  - 货币: {payment.currency}")
        print(f"  - 状态: {payment.status}")
        print(f"  - Checkout ID: {payment.creem_checkout_id}")
        print(f"  - 创建时间: {payment.created_at}")
        
        # 计算创建时间差
        time_since_creation = datetime.utcnow() - payment.created_at
        print(f"  - 创建时间差: {time_since_creation}")
        
        # 查找用户信息
        user = User.query.get(payment.user_id)
        if user:
            print(f"\n👤 用户信息:")
            print(f"  - 邮箱: {user.email}")
            
            # 查询用户当前订阅状态
            subscription = Subscription.query.filter_by(user_id=user.id).first()
            if subscription:
                print("\n📋 当前订阅状态:")
                print(f"  - 计划: {subscription.plan}")
                print(f"  - 状态: {subscription.status}")
                print(f"  - 开始日期: {subscription.start_date}")
                print(f"  - 结束日期: {subscription.end_date}")
        
        # 分析状态
        print(f"\n🔍 状态分析:")
        if payment.status == 'pending':
            print("❌ 支付状态为pending - 回调未成功处理")
            if time_since_creation > timedelta(minutes=5):
                print("⚠️  订单创建时间超过5分钟，可能需要手动处理")
        elif payment.status == 'completed':
            print("✅ 支付已完成")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        request_id = sys.argv[1]
        check_order(request_id)
    else:
        print("使用方法: python check_new_order.py <request_id>")
        print("例如: python check_new_order.py user_12_basic_1756299016")
