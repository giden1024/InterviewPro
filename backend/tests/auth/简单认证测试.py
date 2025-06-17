#!/usr/bin/env python3
"""
简单认证功能测试
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# 测试用户注册
print("测试用户注册...")
register_data = {
    "email": "simple_test@example.com",
    "password": "password123",
    "username": "简单测试用户"
}

try:
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    if response.status_code == 201:
        print("✅ 注册成功!")
        data = response.json()
        token = data['data']['access_token']
        
        # 测试用户信息获取
        print("\n测试获取用户信息...")
        headers = {'Authorization': f'Bearer {token}'}
        profile_response = requests.get(f"{BASE_URL}/api/v1/auth/profile", headers=headers)
        print(f"状态码: {profile_response.status_code}")
        print(f"响应: {profile_response.text}")
        
    else:
        print("❌ 注册失败")

except Exception as e:
    print(f"请求异常: {e}")
    
# 测试健康检查
print("\n测试健康检查...")
health_response = requests.get(f"{BASE_URL}/health")
print(f"健康检查: {health_response.text}") 