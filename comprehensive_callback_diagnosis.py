#!/usr/bin/env python3
"""
综合回调诊断工具 - 全面诊断回调失败的原因
"""
import requests
import time
import json
import subprocess
from datetime import datetime
import sys
import os
sys.path.append('/Users/mayuyang/InterviewPro/backend')

from app import create_app
from app.models.subscription import PaymentHistory
from sqlalchemy import desc

class ComprehensiveCallbackDiagnosis:
    def __init__(self):
        self.app = create_app()
        
    def test_ngrok_connectivity(self):
        """测试ngrok连接性"""
        print("🔍 测试ngrok连接性...")
        print("=" * 60)
        
        # 1. 检查ngrok隧道状态
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                if tunnels:
                    tunnel = tunnels[0]
                    public_url = tunnel.get('public_url')
                    print(f"✅ ngrok隧道正常: {public_url}")
                    
                    # 2. 测试基本连接
                    try:
                        test_response = requests.get(public_url, timeout=10)
                        print(f"✅ 基本连接正常: {test_response.status_code}")
                    except Exception as e:
                        print(f"❌ 基本连接失败: {e}")
                        return False
                    
                    # 3. 测试回调端点
                    callback_url = f"{public_url}/api/v1/billing/callback"
                    try:
                        callback_response = requests.get(
                            f"{callback_url}?test=diagnosis",
                            timeout=10
                        )
                        print(f"✅ 回调端点可访问: {callback_response.status_code}")
                    except Exception as e:
                        print(f"❌ 回调端点不可访问: {e}")
                        return False
                    
                    return True, public_url
                else:
                    print("❌ 没有活跃的ngrok隧道")
                    return False, None
            else:
                print(f"❌ 无法获取ngrok状态: {response.status_code}")
                return False, None
        except Exception as e:
            print(f"❌ ngrok API不可访问: {e}")
            return False, None
    
    def test_external_callback(self, public_url):
        """从外部测试回调"""
        print("\n🌐 从外部测试回调...")
        print("=" * 60)
        
        callback_url = f"{public_url}/api/v1/billing/callback"
        test_params = {
            'checkout_id': 'test_diagnosis_' + str(int(time.time())),
            'request_id': 'user_12_basic_diagnosis_' + str(int(time.time())),
            'signature': 'test_diagnosis_signature'
        }
        
        print(f"📡 测试URL: {callback_url}")
        print(f"📋 测试参数: {test_params}")
        
        try:
            # 记录发送时间
            send_time = datetime.utcnow()
            print(f"🕐 发送时间: {send_time}")
            
            response = requests.get(callback_url, params=test_params, timeout=15)
            receive_time = datetime.utcnow()
            
            print(f"📊 响应状态: {response.status_code}")
            print(f"📄 响应内容: {response.text[:200]}...")
            print(f"⏱️  响应时间: {(receive_time - send_time).total_seconds():.2f}秒")
            
            return True, test_params['request_id']
        except Exception as e:
            print(f"❌ 外部测试失败: {e}")
            return False, None
    
    def check_backend_logs(self, test_request_id):
        """检查后端是否收到请求"""
        print(f"\n📋 检查后端日志...")
        print("=" * 60)
        
        # 等待一下让日志写入
        time.sleep(2)
        
        # 检查ngrok请求日志
        try:
            response = requests.get("http://127.0.0.1:4040/api/requests/http", timeout=5)
            if response.status_code == 200:
                requests_log = response.json().get('requests', [])
                
                # 查找我们的测试请求
                found_request = False
                for req in requests_log[-10:]:  # 检查最近10个请求
                    uri = req.get('request', {}).get('uri', '')
                    if test_request_id in uri:
                        found_request = True
                        print(f"✅ 在ngrok日志中找到测试请求")
                        print(f"   URI: {uri}")
                        print(f"   状态: {req.get('response', {}).get('status_code', 'N/A')}")
                        break
                
                if not found_request:
                    print(f"❌ 在ngrok日志中未找到测试请求")
                    print("   这可能表明请求没有通过ngrok到达后端")
                    
                    # 显示最近的请求
                    print("\n📋 最近的ngrok请求:")
                    for i, req in enumerate(requests_log[-5:], 1):
                        uri = req.get('request', {}).get('uri', '')
                        status = req.get('response', {}).get('status_code', 'N/A')
                        print(f"   {i}. {uri} - {status}")
                
        except Exception as e:
            print(f"❌ 检查ngrok日志失败: {e}")
    
    def check_creem_webhook_requirements(self):
        """检查Creem.io webhook要求"""
        print(f"\n🔧 检查Creem.io webhook要求...")
        print("=" * 60)
        
        print("📋 Creem.io webhook常见问题:")
        print("1. ✅ HTTPS要求: 我们使用ngrok HTTPS")
        print("2. ✅ 端点可访问: 已验证外网可访问")
        print("3. ❓ 响应时间: webhook需要在30秒内响应")
        print("4. ❓ 响应格式: 需要返回2xx状态码")
        print("5. ❓ IP白名单: 某些服务商有IP限制")
        print("6. ❓ User-Agent: 检查是否有特定的User-Agent要求")
        
        print("\n💡 建议检查项:")
        print("- Creem.io控制台中的webhook日志")
        print("- webhook的重试机制设置")
        print("- 是否有IP地址限制")
        print("- webhook的超时设置")
    
    def check_pending_orders(self):
        """检查pending订单"""
        print(f"\n📊 检查pending订单...")
        print("=" * 60)
        
        with self.app.app_context():
            pending_payments = PaymentHistory.query.filter_by(
                status='pending'
            ).order_by(desc(PaymentHistory.created_at)).limit(5).all()
            
            if pending_payments:
                print(f"发现 {len(pending_payments)} 个pending订单:")
                for payment in pending_payments:
                    time_diff = datetime.utcnow() - payment.created_at
                    print(f"  📝 {payment.request_id}")
                    print(f"     金额: ¥{payment.amount} | 等待: {time_diff}")
                    print(f"     Checkout ID: {payment.creem_checkout_id}")
            else:
                print("✅ 没有pending订单")
    
    def run_comprehensive_diagnosis(self):
        """运行综合诊断"""
        print("🚀 开始综合回调诊断...")
        print("=" * 80)
        
        # 1. 测试ngrok连接
        ngrok_ok, public_url = self.test_ngrok_connectivity()
        if not ngrok_ok:
            print("❌ ngrok连接问题，无法继续诊断")
            return
        
        # 2. 外部回调测试
        external_ok, test_request_id = self.test_external_callback(public_url)
        if external_ok and test_request_id:
            # 3. 检查后端日志
            self.check_backend_logs(test_request_id)
        
        # 4. 检查webhook要求
        self.check_creem_webhook_requirements()
        
        # 5. 检查pending订单
        self.check_pending_orders()
        
        print("\n" + "=" * 80)
        print("🎯 诊断完成！请检查上述结果并对比Creem.io控制台的webhook日志。")

def main():
    diagnosis = ComprehensiveCallbackDiagnosis()
    diagnosis.run_comprehensive_diagnosis()

if __name__ == '__main__':
    main()
