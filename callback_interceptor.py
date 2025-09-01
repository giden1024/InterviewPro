#!/usr/bin/env python3
"""
回调拦截器 - 记录所有到达我们服务器的回调请求
这个工具会监听特定端口并记录所有HTTP请求的详细信息
"""
import http.server
import socketserver
import json
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import threading
import time

class CallbackInterceptor(http.server.BaseHTTPRequestHandler):
    """回调请求拦截器"""
    
    def log_request_details(self):
        """记录请求详细信息"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        print("=" * 100)
        print(f"🔔 CALLBACK INTERCEPTED AT {timestamp}")
        print("=" * 100)
        
        # 基本请求信息
        print(f"🌐 Method: {self.command}")
        print(f"🔗 Path: {self.path}")
        print(f"🌍 Client: {self.client_address[0]}:{self.client_address[1]}")
        print(f"📡 Protocol: {self.request_version}")
        
        # 解析URL和参数
        parsed_url = urlparse(self.path)
        print(f"📍 Parsed Path: {parsed_url.path}")
        print(f"🔍 Query String: {parsed_url.query}")
        
        if parsed_url.query:
            params = parse_qs(parsed_url.query)
            print("📋 Parameters:")
            for key, values in params.items():
                print(f"  - {key}: {values[0] if values else 'None'}")
        
        # 请求头
        print("🌐 Headers:")
        for header_name, header_value in self.headers.items():
            print(f"  - {header_name}: {header_value}")
        
        # 如果是POST请求，读取body
        if self.command == 'POST':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    print(f"📝 POST Data: {post_data.decode('utf-8', errors='ignore')}")
            except Exception as e:
                print(f"❌ Error reading POST data: {e}")
        
        print("=" * 100)
        
        # 保存到日志文件
        self.save_to_log()
    
    def save_to_log(self):
        """保存到日志文件"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'method': self.command,
            'path': self.path,
            'client_ip': self.client_address[0],
            'headers': dict(self.headers),
            'query_params': dict(parse_qs(urlparse(self.path).query)) if urlparse(self.path).query else {}
        }
        
        try:
            with open('callback_intercept.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"❌ Error saving to log file: {e}")
    
    def do_GET(self):
        """处理GET请求"""
        self.log_request_details()
        
        # 返回成功响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'intercepted',
            'message': 'Callback intercepted successfully',
            'timestamp': datetime.utcnow().isoformat()
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """处理POST请求"""
        self.log_request_details()
        
        # 返回成功响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'intercepted',
            'message': 'Callback intercepted successfully',
            'timestamp': datetime.utcnow().isoformat()
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """重写日志消息以避免默认日志输出"""
        pass

def start_interceptor(port=5003):
    """启动回调拦截器"""
    print(f"🚀 启动回调拦截器在端口 {port}")
    print(f"📝 日志将保存到 callback_intercept.log")
    print(f"🔗 拦截URL: http://localhost:{port}/api/v1/billing/callback")
    print("按 Ctrl+C 停止拦截器")
    print("=" * 80)
    
    try:
        with socketserver.TCPServer(("", port), CallbackInterceptor) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 拦截器已停止")
    except Exception as e:
        print(f"❌ 拦截器错误: {e}")

def monitor_log_file():
    """实时监控日志文件"""
    import subprocess
    import sys
    
    print("🔍 开始监控回调拦截日志...")
    print("=" * 60)
    
    try:
        # 使用tail -f监控日志文件
        process = subprocess.Popen(['tail', '-f', 'callback_intercept.log'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 universal_newlines=True)
        
        for line in process.stdout:
            try:
                log_entry = json.loads(line.strip())
                print(f"📅 {log_entry['timestamp']}")
                print(f"🌐 {log_entry['method']} {log_entry['path']}")
                print(f"🌍 来自: {log_entry['client_ip']}")
                if log_entry.get('query_params'):
                    print(f"📋 参数: {log_entry['query_params']}")
                print("-" * 40)
            except json.JSONDecodeError:
                print(f"Raw log: {line.strip()}")
                
    except FileNotFoundError:
        print("❌ 日志文件不存在，请先启动拦截器")
    except KeyboardInterrupt:
        print("\n🛑 停止监控")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'monitor':
            monitor_log_file()
        elif sys.argv[1] == 'start':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 5003
            start_interceptor(port)
        else:
            print("使用方法:")
            print("  python callback_interceptor.py start [port]  # 启动拦截器")
            print("  python callback_interceptor.py monitor       # 监控日志")
    else:
        start_interceptor()
