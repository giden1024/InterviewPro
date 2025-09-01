#!/usr/bin/env python3
"""
分析支付pending状态的根本原因
"""
import sys
import os
sys.path.append('/Users/mayuyang/InterviewPro/backend')

from app import create_app
from app.models.subscription import PaymentHistory
from app.models.user import User
from sqlalchemy import desc
from datetime import datetime, timedelta

def main():
    app = create_app()
    
    with app.app_context():
        print("🔍 分析支付pending状态的原因")
        print("=" * 60)
        
        # 查找用户
        user = User.query.filter_by(email='3938930977@qq.com').first()
        if not user:
            print("❌ 用户不存在")
            return
        
        # 查询最新的pending支付
        latest_pending = PaymentHistory.query.filter_by(
            user_id=user.id, 
            status='pending'
        ).order_by(desc(PaymentHistory.created_at)).first()
        
        if not latest_pending:
            print("✅ 当前没有pending状态的支付")
            return
        
        print(f"💳 最新pending支付分析:")
        print(f"  - Request ID: {latest_pending.request_id}")
        print(f"  - Checkout ID: {latest_pending.creem_checkout_id}")
        print(f"  - 创建时间: {latest_pending.created_at}")
        print(f"  - 距离现在: {datetime.utcnow() - latest_pending.created_at}")
        print()
        
        # 分析可能的原因
        print("🔍 可能的pending原因分析:")
        print()
        
        # 1. 检查时间差
        time_diff = datetime.utcnow() - latest_pending.created_at
        if time_diff > timedelta(minutes=30):
            print("⚠️  1. 支付创建时间过长 (>30分钟)")
            print("   - 可能原因: 用户未完成支付，或Creem.io回调延迟")
        else:
            print("✅ 1. 支付创建时间正常 (<30分钟)")
        
        # 2. 检查ngrok状态
        print("\n🔍 2. 检查ngrok隧道状态:")
        try:
            import requests
            response = requests.get("https://0b0568eb0868.ngrok-free.app", timeout=5)
            if response.status_code == 200:
                print("✅ ngrok隧道正常")
            else:
                print(f"⚠️  ngrok隧道异常: {response.status_code}")
        except Exception as e:
            print(f"❌ ngrok隧道不可访问: {e}")
        
        # 3. 检查回调端点
        print("\n🔍 3. 检查回调端点状态:")
        try:
            callback_url = "https://0b0568eb0868.ngrok-free.app/api/v1/billing/callback"
            response = requests.get(f"{callback_url}?test=1", timeout=5)
            print(f"✅ 回调端点可访问: {response.status_code}")
        except Exception as e:
            print(f"❌ 回调端点不可访问: {e}")
        
        # 4. 分析可能的解决方案
        print("\n💡 可能的解决方案:")
        print("  1. 手动同步支付状态 (已完成)")
        print("  2. 检查Creem.io控制台的回调日志")
        print("  3. 验证签名算法是否正确")
        print("  4. 检查网络连接和防火墙")
        print("  5. 重新配置回调URL")
        
        # 5. 提供具体的回调URL信息
        print(f"\n📋 当前配置信息:")
        print(f"  - 回调URL: https://0b0568eb0868.ngrok-free.app/api/v1/billing/callback")
        print(f"  - 前端URL: http://localhost:3000")
        print(f"  - 支付ID: {latest_pending.request_id}")
        print(f"  - Checkout ID: {latest_pending.creem_checkout_id}")

if __name__ == '__main__':
    main()
