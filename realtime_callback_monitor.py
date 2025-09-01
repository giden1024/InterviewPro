#!/usr/bin/env python3
"""
实时回调监控器 - 监控新的支付回调
"""
import time
import requests
import json
from datetime import datetime, timedelta
import sys
import os
sys.path.append('/Users/mayuyang/InterviewPro/backend')

from app import create_app
from app.models.subscription import PaymentHistory
from sqlalchemy import desc

class RealtimeCallbackMonitor:
    def __init__(self):
        self.last_ngrok_request_count = 0
        self.last_db_check = datetime.utcnow()
        self.app = create_app()
        
    def get_ngrok_requests(self):
        """获取ngrok请求"""
        try:
            response = requests.get("http://127.0.0.1:4040/api/requests/http", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('requests', [])
        except:
            pass
        return []
    
    def check_new_ngrok_requests(self):
        """检查新的ngrok请求"""
        requests_log = self.get_ngrok_requests()
        current_count = len(requests_log)
        
        if current_count > self.last_ngrok_request_count:
            new_requests = requests_log[self.last_ngrok_request_count:]
            print(f"🆕 发现 {len(new_requests)} 个新的ngrok请求:")
            
            for req in new_requests:
                uri = req.get('request', {}).get('uri', '')
                method = req.get('request', {}).get('method', 'N/A')
                status = req.get('response', {}).get('status_code', 'N/A')
                
                print(f"  📡 {method} {uri}")
                print(f"  📊 状态: {status}")
                
                # 检查是否是回调请求
                if '/billing/callback' in uri:
                    print(f"  🔔 ** 支付回调请求! **")
                    # 解析参数
                    if 'request_id=' in uri:
                        import re
                        match = re.search(r'request_id=([^&]+)', uri)
                        if match:
                            request_id = match.group(1)
                            print(f"  📝 Request ID: {request_id}")
                            
                            # 检查是否是我们要监控的订单
                            if 'user_12_basic_1756299016' in request_id:
                                print(f"  🎯 ** 这是我们要监控的新订单回调! **")
                print()
        
        self.last_ngrok_request_count = current_count
    
    def check_new_payments(self):
        """检查新的支付记录"""
        with self.app.app_context():
            # 查找最近创建的支付记录
            recent_payments = PaymentHistory.query.filter(
                PaymentHistory.created_at > self.last_db_check
            ).order_by(desc(PaymentHistory.created_at)).all()
            
            if recent_payments:
                print(f"🆕 发现 {len(recent_payments)} 条新支付记录:")
                for payment in recent_payments:
                    print(f"  📝 Request ID: {payment.request_id}")
                    print(f"  💰 金额: ¥{payment.amount} ({payment.plan})")
                    print(f"  📊 状态: {payment.status}")
                    print(f"  🕐 创建时间: {payment.created_at}")
                    print()
            
            self.last_db_check = datetime.utcnow()
    
    def check_order_status(self, request_id):
        """检查特定订单状态"""
        with self.app.app_context():
            payment = PaymentHistory.query.filter_by(request_id=request_id).first()
            if payment:
                time_since_creation = datetime.utcnow() - payment.created_at
                status_icon = "✅" if payment.status == 'completed' else "⏳" if payment.status == 'pending' else "❌"
                print(f"📋 订单 {request_id}:")
                print(f"  {status_icon} 状态: {payment.status}")
                print(f"  ⏱️  等待时间: {time_since_creation}")
                return payment.status
            else:
                print(f"❌ 未找到订单: {request_id}")
                return None
    
    def monitor_realtime(self, target_request_id=None):
        """实时监控"""
        print(f"🔍 开始实时监控支付回调...")
        if target_request_id:
            print(f"🎯 重点监控订单: {target_request_id}")
        print("按 Ctrl+C 停止监控")
        print("=" * 80)
        
        try:
            while True:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"🕐 {current_time} - 监控中...")
                
                # 检查ngrok新请求
                self.check_new_ngrok_requests()
                
                # 检查新支付记录
                self.check_new_payments()
                
                # 如果指定了目标订单，检查其状态
                if target_request_id:
                    status = self.check_order_status(target_request_id)
                    if status == 'completed':
                        print(f"🎉 订单 {target_request_id} 已完成！")
                        break
                
                print("-" * 40)
                time.sleep(10)  # 每10秒检查一次
                
        except KeyboardInterrupt:
            print("\n🛑 停止监控")

def main():
    monitor = RealtimeCallbackMonitor()
    
    if len(sys.argv) > 1:
        target_request_id = sys.argv[1]
        monitor.monitor_realtime(target_request_id)
    else:
        monitor.monitor_realtime()

if __name__ == '__main__':
    main()
