#!/usr/bin/env python3
"""
ngrok监控工具 - 监控ngrok隧道状态和请求日志
"""
import requests
import json
import time
from datetime import datetime
import subprocess
import sys

class NgrokMonitor:
    def __init__(self):
        self.ngrok_api_url = "http://127.0.0.1:4040/api"
        
    def get_tunnel_status(self):
        """获取ngrok隧道状态"""
        try:
            response = requests.get(f"{self.ngrok_api_url}/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('tunnels', [])
            else:
                return None
        except Exception as e:
            print(f"❌ 无法连接到ngrok API: {e}")
            return None
    
    def display_tunnel_info(self):
        """显示隧道信息"""
        tunnels = self.get_tunnel_status()
        if not tunnels:
            print("❌ 没有活跃的ngrok隧道")
            return False
        
        print("🚇 ngrok隧道状态:")
        print("=" * 60)
        
        for tunnel in tunnels:
            print(f"📌 名称: {tunnel.get('name', 'N/A')}")
            print(f"🌐 公网URL: {tunnel.get('public_url', 'N/A')}")
            print(f"🔗 本地URL: {tunnel.get('config', {}).get('addr', 'N/A')}")
            print(f"📊 协议: {tunnel.get('proto', 'N/A')}")
            print(f"📈 连接数: {tunnel.get('metrics', {}).get('conns', {}).get('count', 0)}")
            print(f"📤 HTTP请求数: {tunnel.get('metrics', {}).get('http', {}).get('count', 0)}")
            print("-" * 40)
        
        return True
    
    def get_requests_log(self):
        """获取ngrok请求日志"""
        try:
            response = requests.get(f"{self.ngrok_api_url}/requests/http", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('requests', [])
            else:
                return []
        except Exception as e:
            print(f"❌ 获取请求日志失败: {e}")
            return []
    
    def display_recent_requests(self, limit=10):
        """显示最近的请求"""
        requests_log = self.get_requests_log()
        if not requests_log:
            print("📝 没有找到请求日志")
            return
        
        print(f"📋 最近 {min(limit, len(requests_log))} 个请求:")
        print("=" * 80)
        
        for i, req in enumerate(requests_log[-limit:], 1):
            started_at = req.get('started_at', '')
            if started_at:
                try:
                    timestamp = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    local_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    local_time = started_at
            else:
                local_time = 'Unknown'
            
            print(f"{i}. 🕐 {local_time}")
            print(f"   🌐 {req.get('request', {}).get('method', 'N/A')} {req.get('request', {}).get('uri', 'N/A')}")
            print(f"   🌍 来自: {req.get('request', {}).get('headers', {}).get('x-forwarded-for', ['Unknown'])[0]}")
            print(f"   📊 状态: {req.get('response', {}).get('status_code', 'N/A')}")
            print(f"   ⏱️  耗时: {req.get('duration', 0) / 1000000:.2f}ms")
            
            # 检查是否是回调请求
            uri = req.get('request', {}).get('uri', '')
            if '/billing/callback' in uri:
                print(f"   🔔 ** 这是一个支付回调请求! **")
                # 显示查询参数
                query_params = req.get('request', {}).get('query_params', {})
                if query_params:
                    print(f"   📋 参数:")
                    for key, values in query_params.items():
                        print(f"      - {key}: {values[0] if values else 'None'}")
            
            print("-" * 40)
    
    def monitor_realtime(self, interval=5):
        """实时监控"""
        print(f"🔍 开始实时监控ngrok (每{interval}秒刷新)")
        print("按 Ctrl+C 停止监控")
        print("=" * 80)
        
        last_request_count = 0
        
        try:
            while True:
                # 清屏
                subprocess.run(['clear'], check=True)
                
                print(f"🔍 ngrok实时监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 80)
                
                # 显示隧道状态
                if not self.display_tunnel_info():
                    print("⚠️  ngrok隧道未启动")
                    time.sleep(interval)
                    continue
                
                print()
                
                # 显示最近请求
                requests_log = self.get_requests_log()
                current_request_count = len(requests_log)
                
                if current_request_count > last_request_count:
                    new_requests = current_request_count - last_request_count
                    print(f"🆕 发现 {new_requests} 个新请求!")
                
                self.display_recent_requests(5)
                last_request_count = current_request_count
                
                print(f"\n⏰ 下次刷新: {interval}秒后...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 停止监控")
    
    def check_callback_url(self):
        """检查回调URL是否可访问"""
        tunnels = self.get_tunnel_status()
        if not tunnels:
            print("❌ 没有活跃的ngrok隧道")
            return
        
        for tunnel in tunnels:
            public_url = tunnel.get('public_url')
            if public_url and 'https://' in public_url:
                callback_url = f"{public_url}/api/v1/billing/callback"
                print(f"🧪 测试回调URL: {callback_url}")
                
                try:
                    response = requests.get(f"{callback_url}?test=ngrok_monitor", timeout=10)
                    print(f"✅ 回调URL可访问 - 状态码: {response.status_code}")
                    print(f"📄 响应: {response.text[:100]}...")
                except Exception as e:
                    print(f"❌ 回调URL不可访问: {e}")
                
                break

def main():
    monitor = NgrokMonitor()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python ngrok_monitor.py status    # 显示隧道状态")
        print("  python ngrok_monitor.py requests  # 显示最近请求")
        print("  python ngrok_monitor.py monitor   # 实时监控")
        print("  python ngrok_monitor.py test      # 测试回调URL")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        monitor.display_tunnel_info()
    elif command == "requests":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        monitor.display_recent_requests(limit)
    elif command == "monitor":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        monitor.monitor_realtime(interval)
    elif command == "test":
        monitor.check_callback_url()
    else:
        print("❌ 无效的命令")

if __name__ == '__main__':
    main()
