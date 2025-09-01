#!/usr/bin/env python3
"""
调试支付回调流程
"""
import sys
import os
import requests
import hashlib
import hmac
from urllib.parse import urlencode

def generate_creem_signature(data, secret_key):
    """生成Creem.io签名"""
    # 按字母顺序排序参数
    sorted_params = sorted(data.items())
    query_string = urlencode(sorted_params)
    
    # 使用HMAC-SHA256生成签名
    signature = hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature

def test_payment_callback():
    """测试支付回调"""
    print("🔍 测试支付回调流程")
    print("=" * 60)
    
    # 模拟回调参数
    callback_data = {
        'checkout_id': 'ch_22niQO9ddHjivQEhDXrFxA',
        'order_id': 'ord_5JxAWk5ee6CRfrVDgj751z',
        'customer_id': 'cust_tldWJMuhcJzHUjuU4EYq1',
        'product_id': 'prod_1UsU2rK5AiyVINJuHWnPyy',
        'request_id': 'user_2_basic_1756199137'
    }
    
    # 假设的密钥（需要从环境变量获取真实的）
    secret_key = "test_secret_key"
    
    # 生成签名
    signature = generate_creem_signature(callback_data, secret_key)
    callback_data['signature'] = signature
    
    print(f"📋 回调参数:")
    for key, value in callback_data.items():
        print(f"   {key}: {value}")
    print()
    
    # 测试回调URL
    callback_url = "http://localhost:5000/api/v1/billing/callback"
    
    try:
        print(f"🔄 发送回调请求到: {callback_url}")
        response = requests.get(callback_url, params=callback_data, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('text/html'):
            print(f"📊 响应内容 (HTML):")
            # 只显示前500字符
            content = response.text[:500]
            print(f"   {content}...")
        else:
            print(f"📊 响应内容 (JSON):")
            try:
                print(f"   {response.json()}")
            except:
                print(f"   {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 回调请求失败: {e}")
    
    print()
    
    # 测试webhook回调
    webhook_url = "http://localhost:5000/api/v1/billing/webhook"
    webhook_data = {
        "event_type": "payment.completed",
        "data": {
            "checkout_id": "ch_22niQO9ddHjivQEhDXrFxA",
            "order_id": "ord_5JxAWk5ee6CRfrVDgj751z",
            "customer_id": "cust_tldWJMuhcJzHUjuU4EYq1",
            "product_id": "prod_1UsU2rK5AiyVINJuHWnPyy",
            "request_id": "user_2_basic_1756199137",
            "amount": 29.00,
            "currency": "CNY",
            "status": "completed"
        }
    }
    
    try:
        print(f"🔄 发送webhook请求到: {webhook_url}")
        response = requests.post(
            webhook_url, 
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Webhook响应状态码: {response.status_code}")
        print(f"📊 Webhook响应内容:")
        try:
            print(f"   {response.json()}")
        except:
            print(f"   {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook请求失败: {e}")

def check_backend_status():
    """检查后端状态"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"⚠️ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 后端服务不可用: {e}")
        return False

if __name__ == "__main__":
    print("🔧 支付回调调试工具")
    print("=" * 60)
    
    # 检查后端状态
    if not check_backend_status():
        print("请先启动后端服务")
        sys.exit(1)
    
    print()
    test_payment_callback()
