#!/usr/bin/env python3
"""
InterviewGenius AI 项目状态检查脚本
检查所有核心功能是否正常工作
"""
import requests
import socketio
import time
import sys
import os

def print_status(status, message):
    """打印状态信息"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {message}")
    return status

def check_api_health():
    """检查API健康状态"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return print_status(True, f"API健康检查正常: {data.get('status', 'unknown')}")
        else:
            return print_status(False, f"API响应异常: {response.status_code}")
    except Exception as e:
        return print_status(False, f"API连接失败: {e}")

def check_auth_endpoints():
    """检查认证相关端点"""
    try:
        # 测试注册
        test_email = f"test_{int(time.time())}@example.com"
        register_data = {
            "email": test_email,
            "password": "password123",
            "username": "Test User"
        }
        
        response = requests.post(
            'http://localhost:5000/api/v1/auth/register',
            json=register_data,
            timeout=5
        )
        
        if response.status_code == 201:
            print_status(True, "用户注册功能正常")
            
            # 测试登录
            login_data = {
                "email": test_email,
                "password": "password123"
            }
            
            login_response = requests.post(
                'http://localhost:5000/api/v1/auth/login',
                json=login_data,
                timeout=5
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                token = login_result.get('data', {}).get('access_token')
                
                if token:
                    print_status(True, "用户登录功能正常")
                    
                    # 测试获取用户信息
                    headers = {'Authorization': f'Bearer {token}'}
                    profile_response = requests.get(
                        'http://localhost:5000/api/v1/auth/profile',
                        headers=headers,
                        timeout=5
                    )
                    
                    if profile_response.status_code == 200:
                        return print_status(True, "用户信息获取正常")
                    else:
                        return print_status(False, "用户信息获取失败")
                else:
                    return print_status(False, "Token获取失败")
            else:
                return print_status(False, f"登录失败: {login_response.status_code}")
        else:
            return print_status(False, f"注册失败: {response.status_code}")
            
    except Exception as e:
        return print_status(False, f"认证功能测试失败: {e}")

def check_websocket():
    """检查WebSocket功能"""
    try:
        sio = socketio.Client()
        
        connected = False
        test_response_received = False
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
            sio.emit('test_message', {
                'message': 'Project check test',
                'timestamp': time.time()
            })
        
        @sio.event
        def connected(data):
            pass
        
        @sio.event
        def test_response(data):
            nonlocal test_response_received
            test_response_received = True
            sio.disconnect()
        
        @sio.event
        def error(data):
            print(f"WebSocket错误: {data}")
        
        sio.connect('http://localhost:5000', wait_timeout=5)
        time.sleep(2)
        
        if connected and test_response_received:
            return print_status(True, "WebSocket功能正常")
        elif connected:
            return print_status(False, "WebSocket连接成功但消息处理异常")
        else:
            return print_status(False, "WebSocket连接失败")
            
    except Exception as e:
        return print_status(False, f"WebSocket测试失败: {e}")
    finally:
        try:
            if sio.connected:
                sio.disconnect()
        except:
            pass

def check_project_structure():
    """检查项目结构"""
    required_files = [
        'backend/app/__init__.py',
        'backend/app/models/user.py',
        'backend/app/api/auth.py',
        'backend/app/websocket/handlers.py',
        'backend/requirements.txt',
        'backend/run.py',
        'docker-compose.yml',
        'nginx.conf',
        'docs/开发进度.md',
        'README.md'
    ]
    
    all_exists = True
    for file_path in required_files:
        full_path = os.path.join('..', file_path) if not file_path.startswith('backend/') else file_path
        if os.path.exists(full_path):
            print_status(True, f"文件存在: {file_path}")
        else:
            print_status(False, f"文件缺失: {file_path}")
            all_exists = False
    
    return all_exists

def main():
    """主检查函数"""
    print("🚀 InterviewGenius AI 项目状态检查")
    print("=" * 50)
    
    # 检查项目结构
    print("\n📁 项目结构检查:")
    structure_ok = check_project_structure()
    
    # 检查API服务
    print("\n🌐 API服务检查:")
    api_ok = check_api_health()
    
    if api_ok:
        # 检查认证功能
        print("\n🔐 认证功能检查:")
        auth_ok = check_auth_endpoints()
        
        # 检查WebSocket
        print("\n🔌 WebSocket功能检查:")
        ws_ok = check_websocket()
    else:
        print("\n❌ API服务未启动，跳过功能测试")
        auth_ok = False
        ws_ok = False
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 检查总结:")
    
    total_checks = 4
    passed_checks = sum([structure_ok, api_ok, auth_ok, ws_ok])
    
    print(f"✅ 通过检查: {passed_checks}/{total_checks}")
    print(f"📈 完成度: {(passed_checks/total_checks)*100:.1f}%")
    
    if passed_checks == total_checks:
        print("🎉 所有检查通过！项目状态良好。")
        return 0
    else:
        print("⚠️  部分检查未通过，请检查相关功能。")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 