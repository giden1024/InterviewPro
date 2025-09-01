#!/usr/bin/env python3
"""
检查高级版订单 user_12_premium_1756204962 的详细状态
"""
import sys
import os
sys.path.append('/Users/mayuyang/InterviewPro/backend')

from app import create_app
from app.models.subscription import Subscription, PaymentHistory
from app.models.user import User
from sqlalchemy import desc
from datetime import datetime, timedelta

def main():
    app = create_app()
    
    with app.app_context():
        request_id = "user_12_premium_1756204962"
        print(f"🔍 检查高级版订单: {request_id}")
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
        print(f"  - Order ID: {getattr(payment, 'creem_order_id', 'N/A')}")
        print(f"  - Customer ID: {getattr(payment, 'creem_customer_id', 'N/A')}")
        print(f"  - 创建时间: {payment.created_at}")
        if hasattr(payment, 'payment_date') and payment.payment_date:
            print(f"  - 支付时间: {payment.payment_date}")
        print()
        
        # 查找用户信息
        user = User.query.get(payment.user_id)
        if user:
            print(f"👤 用户信息:")
            print(f"  - 邮箱: {user.email}")
            print(f"  - 用户名: {user.username}")
            print()
            
            # 查询用户当前订阅状态
            subscription = Subscription.query.filter_by(user_id=user.id).first()
            if subscription:
                print("📋 当前订阅状态:")
                print(f"  - 计划: {subscription.plan}")
                print(f"  - 状态: {subscription.status}")
                print(f"  - 开始日期: {subscription.start_date}")
                print(f"  - 结束日期: {subscription.end_date}")
                print()
        
        # 分析问题
        print("🔍 问题分析:")
        time_since_creation = datetime.utcnow() - payment.created_at
        print(f"  - 订单创建时间: {time_since_creation} 前")
        
        if payment.status == 'pending':
            print("  ❌ 支付状态为 pending 的可能原因:")
            print("    1. 用户未完成支付流程")
            print("    2. Creem.io 回调未到达我们的服务器")
            print("    3. 回调处理过程中出现错误")
            print("    4. 网络连接问题")
            
            if time_since_creation > timedelta(minutes=30):
                print("  ⚠️  订单创建时间超过30分钟，可能需要手动处理")
            
        elif payment.status == 'completed':
            print("  ✅ 支付已完成")
            if subscription and subscription.plan != payment.plan:
                print("  ⚠️  订阅计划与支付记录不匹配")
        
        # 检查是否有回调日志
        print("\n📋 建议的处理步骤:")
        if payment.status == 'pending':
            print("  1. 检查 Creem.io 控制台的支付状态")
            print("  2. 查看后端日志是否有回调记录")
            print("  3. 使用模拟回调测试功能")
            print("  4. 如确认支付成功，可手动更新状态")
        
        print(f"\n🛠️  快速修复命令:")
        print(f"  python payment_callback_monitor.py simulate {user.email if user else 'unknown'} {request_id}")

if __name__ == '__main__':
    main()
