#!/usr/bin/env python3
"""
支付回调日志监控工具
实时监控支付回调的处理过程
"""
import sys
import os
import time
import requests
import json
from datetime import datetime
sys.path.append('/Users/mayuyang/InterviewPro/backend')

from app import create_app
from app.models.subscription import PaymentHistory
from app.models.user import User
from sqlalchemy import desc

class PaymentCallbackMonitor:
    def __init__(self):
        self.app = create_app()
        self.last_check = datetime.utcnow()
        
    def check_new_payments(self):
        """检查新的支付记录"""
        with self.app.app_context():
            # 查找最近创建的支付记录
            recent_payments = PaymentHistory.query.filter(
                PaymentHistory.created_at > self.last_check
            ).order_by(desc(PaymentHistory.created_at)).all()
            
            if recent_payments:
                print(f"\n🆕 发现 {len(recent_payments)} 条新支付记录:")
                for payment in recent_payments:
                    user = User.query.get(payment.user_id)
                    print(f"  📋 Request ID: {payment.request_id}")
                    print(f"  👤 用户: {user.email if user else 'Unknown'}")
                    print(f"  💰 金额: ¥{payment.amount} ({payment.plan})")
                    print(f"  📊 状态: {payment.status}")
                    print(f"  🕐 创建时间: {payment.created_at}")
                    print(f"  🔑 Checkout ID: {payment.creem_checkout_id}")
                    print()
            
            self.last_check = datetime.utcnow()
    
    def test_callback_endpoint(self):
        """测试回调端点可用性"""
        try:
            url = "https://0b0568eb0868.ngrok-free.app/api/v1/billing/callback"
            response = requests.get(f"{url}?test=monitor", timeout=5)
            status = "✅ 可访问" if response.status_code in [200, 400] else f"⚠️  异常 ({response.status_code})"
            print(f"🌐 回调端点状态: {status}")
            return True
        except Exception as e:
            print(f"❌ 回调端点不可访问: {e}")
            return False
    
    def simulate_callback(self, user_email, request_id=None):
        """模拟回调测试"""
        with self.app.app_context():
            user = User.query.filter_by(email=user_email).first()
            if not user:
                print(f"❌ 用户 {user_email} 不存在")
                return
            
            if not request_id:
                # 查找最新的pending支付
                payment = PaymentHistory.query.filter_by(
                    user_id=user.id, 
                    status='pending'
                ).order_by(desc(PaymentHistory.created_at)).first()
                
                if not payment:
                    print(f"❌ 用户 {user_email} 没有pending支付记录")
                    return
                request_id = payment.request_id
                checkout_id = payment.creem_checkout_id
            else:
                payment = PaymentHistory.query.filter_by(request_id=request_id).first()
                if not payment:
                    print(f"❌ 找不到支付记录: {request_id}")
                    return
                checkout_id = payment.creem_checkout_id
            
            print(f"🧪 模拟回调测试:")
            print(f"  📧 用户: {user_email}")
            print(f"  📝 Request ID: {request_id}")
            print(f"  🔑 Checkout ID: {checkout_id}")
            
            # 构造回调参数
            callback_params = {
                'checkout_id': checkout_id,
                'order_id': f'ord_test_{int(time.time())}',
                'customer_id': f'cust_test_{user.id}',
                'product_id': 'prod_1UsU2rK5AiyVINJuHWnPyy',
                'request_id': request_id,
                'signature': 'test_signature_for_development'
            }
            
            try:
                url = "https://0b0568eb0868.ngrok-free.app/api/v1/billing/callback"
                response = requests.get(url, params=callback_params, timeout=10)
                
                print(f"📡 回调请求发送")
                print(f"🔄 响应状态: {response.status_code}")
                print(f"📄 响应内容: {response.text[:200]}...")
                
                if response.status_code == 200:
                    print("✅ 回调处理成功")
                else:
                    print(f"⚠️  回调处理异常: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 回调请求失败: {e}")
    
    def monitor_user_payments(self, user_email):
        """监控特定用户的支付状态"""
        with self.app.app_context():
            user = User.query.filter_by(email=user_email).first()
            if not user:
                print(f"❌ 用户 {user_email} 不存在")
                return
            
            print(f"👤 监控用户: {user_email} (ID: {user.id})")
            print("=" * 60)
            
            # 显示最近5条支付记录
            payments = PaymentHistory.query.filter_by(user_id=user.id)\
                .order_by(desc(PaymentHistory.created_at)).limit(5).all()
            
            if payments:
                print("💳 最近5条支付记录:")
                for i, payment in enumerate(payments, 1):
                    status_icon = "✅" if payment.status == 'completed' else "⏳" if payment.status == 'pending' else "❌"
                    print(f"  {i}. {status_icon} {payment.request_id}")
                    print(f"     状态: {payment.status} | 金额: ¥{payment.amount} | 时间: {payment.created_at}")
                    
                    if payment.status == 'pending':
                        time_diff = datetime.utcnow() - payment.created_at
                        print(f"     ⏱️  等待时间: {time_diff}")
            else:
                print("❌ 没有支付记录")

def main():
    monitor = PaymentCallbackMonitor()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python payment_callback_monitor.py monitor <user_email>  # 监控用户支付")
        print("  python payment_callback_monitor.py test                  # 测试回调端点")
        print("  python payment_callback_monitor.py simulate <user_email> # 模拟回调")
        return
    
    command = sys.argv[1]
    
    if command == "monitor" and len(sys.argv) >= 3:
        user_email = sys.argv[2]
        print(f"🔍 开始监控用户 {user_email} 的支付状态...")
        monitor.monitor_user_payments(user_email)
        
    elif command == "test":
        print("🧪 测试回调端点...")
        monitor.test_callback_endpoint()
        
    elif command == "simulate" and len(sys.argv) >= 3:
        user_email = sys.argv[2]
        request_id = sys.argv[3] if len(sys.argv) >= 4 else None
        print(f"🧪 模拟回调测试...")
        monitor.simulate_callback(user_email, request_id)
        
    else:
        print("❌ 无效的命令")

if __name__ == '__main__':
    main()
