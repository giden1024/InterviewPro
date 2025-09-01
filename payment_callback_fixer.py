#!/usr/bin/env python3
"""
支付回调问题修复工具
"""
import sys
import os
import requests
import json
from datetime import datetime

def check_backend_status(port=5002):
    """检查后端服务状态"""
    try:
        response = requests.get(f"http://localhost:{port}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ 后端服务正常运行 (端口 {port})")
            return True
        else:
            print(f"⚠️ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 后端服务不可用: {e}")
        return False

def get_ngrok_url():
    """获取ngrok公网URL"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json()['tunnels']
            for tunnel in tunnels:
                if tunnel['proto'] == 'https':
                    url = tunnel['public_url']
                    print(f"🌐 Ngrok公网URL: {url}")
                    return url
            print("❌ 未找到HTTPS隧道")
            return None
        else:
            print(f"❌ 无法获取ngrok状态: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ngrok不可用: {e}")
        return None

def test_callback_endpoint(base_url, port=5002):
    """测试回调端点"""
    if base_url:
        callback_url = f"{base_url}/api/v1/billing/callback"
    else:
        callback_url = f"http://localhost:{port}/api/v1/billing/callback"
    
    print(f"🔄 测试回调端点: {callback_url}")
    
    # 模拟回调参数
    test_params = {
        'checkout_id': 'test_checkout_123',
        'order_id': 'test_order_456',
        'customer_id': 'test_customer_789',
        'product_id': 'test_product_abc',
        'request_id': 'user_2_basic_test',
        'signature': 'test_signature_xyz'
    }
    
    try:
        response = requests.get(callback_url, params=test_params, timeout=10)
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
                print(f"📊 响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📊 响应内容: {response.text[:200]}...")
        else:
            print(f"📊 响应内容: {response.text[:200]}...")
        
        return response.status_code in [200, 400]  # 400也算正常，说明端点可达
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 回调测试失败: {e}")
        return False

def sync_user_payment(user_email, request_id, port=5002):
    """同步用户支付状态"""
    print(f"🔄 同步用户支付状态: {user_email}")
    
    # 首先登录获取token
    login_url = f"http://localhost:{port}/api/v1/auth/login"
    login_data = {
        "email": user_email,
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(login_url, json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['access_token']
                print("✅ 登录成功")
                
                # 调用同步API
                sync_url = f"http://localhost:{port}/api/v1/billing/sync-payment/{request_id}"
                headers = {'Authorization': f'Bearer {token}'}
                
                sync_response = requests.post(sync_url, headers=headers, timeout=10)
                print(f"📊 同步响应状态码: {sync_response.status_code}")
                
                if sync_response.status_code == 200:
                    sync_data = sync_response.json()
                    print(f"✅ 同步成功: {json.dumps(sync_data, indent=2, ensure_ascii=False)}")
                    return True
                else:
                    print(f"❌ 同步失败: {sync_response.text}")
                    return False
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 同步请求失败: {e}")
        return False

def check_user_subscription(user_email, port=5002):
    """检查用户订阅状态"""
    print(f"🔍 检查用户订阅状态: {user_email}")
    
    # 登录获取token
    login_url = f"http://localhost:{port}/api/v1/auth/login"
    login_data = {
        "email": user_email,
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(login_url, json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['access_token']
                
                # 获取订阅状态
                subscription_url = f"http://localhost:{port}/api/v1/billing/subscription"
                headers = {'Authorization': f'Bearer {token}'}
                
                sub_response = requests.get(subscription_url, headers=headers, timeout=10)
                if sub_response.status_code == 200:
                    sub_data = sub_response.json()
                    if sub_data.get('success'):
                        subscription = sub_data['data']['subscription']
                        usage = sub_data['data']['usage']
                        
                        print(f"📋 当前订阅:")
                        print(f"   计划: {subscription['plan']}")
                        print(f"   状态: {subscription['status']}")
                        print(f"   到期时间: {subscription.get('end_date', '无限制')}")
                        
                        print(f"📊 使用情况:")
                        print(f"   面试: {usage['interviews']['used']}/{usage['interviews']['limit']}")
                        print(f"   AI问题: {usage['ai_questions']['used']}/{usage['ai_questions']['limit']}")
                        print(f"   简历分析: {usage['resume_analysis']['used']}/{usage['resume_analysis']['limit']}")
                        
                        return subscription['plan']
                    else:
                        print(f"❌ 获取订阅失败: {sub_data.get('message')}")
                else:
                    print(f"❌ 订阅请求失败: {sub_response.status_code}")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 检查请求失败: {e}")
    
    return None

def main():
    print("🔧 支付回调问题修复工具")
    print("=" * 60)
    
    # 检查后端服务
    if not check_backend_status():
        print("请先启动后端服务: cd backend && python run_complete.py")
        return
    
    print()
    
    # 检查ngrok状态
    ngrok_url = get_ngrok_url()
    print()
    
    # 测试回调端点
    if test_callback_endpoint(ngrok_url):
        print("✅ 回调端点可访问")
    else:
        print("❌ 回调端点不可访问")
    print()
    
    # 检查用户订阅状态
    user_email = "393893095@qq.com"
    current_plan = check_user_subscription(user_email)
    print()
    
    if current_plan == 'free':
        print("⚠️ 用户仍为免费版，尝试同步支付状态...")
        request_id = "user_2_basic_1756199137"
        if sync_user_payment(user_email, request_id):
            print("✅ 支付状态同步成功")
            check_user_subscription(user_email)
        else:
            print("❌ 支付状态同步失败")
    elif current_plan == 'basic':
        print("✅ 用户订阅状态正常")
    else:
        print(f"ℹ️ 用户当前计划: {current_plan}")
    
    print()
    print("🎯 修复建议:")
    
    if ngrok_url:
        callback_url = f"{ngrok_url}/api/v1/billing/callback"
        print(f"1. 在Creem.io控制台配置回调URL: {callback_url}")
    else:
        print("1. 启动ngrok: ngrok http 5002")
        print("2. 在Creem.io控制台配置回调URL")
    
    print("3. 检查Creem.io控制台的回调日志")
    print("4. 验证API密钥配置是否正确")
    print("5. 如需要，使用同步功能手动修复支付状态")

if __name__ == "__main__":
    main()
