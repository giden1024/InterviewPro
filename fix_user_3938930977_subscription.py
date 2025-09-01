#!/usr/bin/env python3
"""
修复用户3938930977@qq.com的订阅状态
"""
import sys
import os
sys.path.append('/Users/mayuyang/InterviewPro/backend')

from app import create_app
from app.models.subscription import Subscription, PaymentHistory
from app.models.user import User
from app import db
from sqlalchemy import desc
from datetime import datetime, timedelta

def main():
    app = create_app()
    
    with app.app_context():
        print("🔧 修复用户: 3938930977@qq.com")
        print("=" * 60)
        
        # 查找用户
        user = User.query.filter_by(email='3938930977@qq.com').first()
        if not user:
            print("❌ 用户不存在")
            return
        
        print(f"✅ 用户ID: {user.id}")
        
        # 查询订阅状态
        subscription = Subscription.query.filter_by(user_id=user.id).first()
        if not subscription:
            print("❌ 未找到订阅记录")
            return
        
        print(f"📋 当前订阅状态: {subscription.plan} - {subscription.status}")
        
        # 查询最新的pending支付记录
        latest_pending = PaymentHistory.query.filter_by(
            user_id=user.id, 
            status='pending'
        ).order_by(desc(PaymentHistory.created_at)).first()
        
        if latest_pending:
            print(f"💳 最新pending支付: {latest_pending.request_id}")
            print(f"   - Checkout ID: {latest_pending.creem_checkout_id}")
            print(f"   - 金额: ¥{latest_pending.amount}")
            print(f"   - 创建时间: {latest_pending.created_at}")
            
            # 手动将最新支付标记为completed
            print("\n🔧 修复操作:")
            latest_pending.status = 'completed'
            print(f"✅ 支付状态更新为: completed")
            
            # 修复订阅状态
            subscription.status = 'active'  # 从cancelled改为active
            subscription.plan = 'basic'
            subscription.start_date = datetime.utcnow()
            subscription.end_date = datetime.utcnow() + timedelta(days=30)
            
            # 重置使用量
            subscription.monthly_interviews_used = 0
            subscription.monthly_ai_questions_used = 0
            subscription.monthly_resume_analysis_used = 0
            subscription.usage_reset_date = datetime.utcnow().replace(day=1)
            
            print(f"✅ 订阅状态更新为: active")
            print(f"✅ 订阅计划: basic")
            print(f"✅ 重置使用量")
            
            # 提交更改
            db.session.commit()
            print("\n🎉 修复完成！")
            
        else:
            print("❌ 未找到pending支付记录")
        
        # 验证修复结果
        print("\n📊 修复后状态:")
        subscription = Subscription.query.filter_by(user_id=user.id).first()
        print(f"  - 计划: {subscription.plan}")
        print(f"  - 状态: {subscription.status}")
        print(f"  - 开始日期: {subscription.start_date}")
        print(f"  - 结束日期: {subscription.end_date}")

if __name__ == '__main__':
    main()
