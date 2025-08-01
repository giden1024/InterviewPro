#!/usr/bin/env python3
"""
调试创建问题API
"""

import requests
import json

def test_create_question():
    """测试创建问题API"""
    
    # 获取token
    print("🔐 获取访问token...")
    auth_response = requests.post(
        "http://localhost:5001/api/v1/dev/create-test-user",
        json={
            "username": "testuser", 
            "email": "test@example.com", 
            "password": "password123"
        }
    )
    
    if auth_response.status_code != 200:
        print(f"❌ 获取token失败: {auth_response.text}")
        return
    
    token = auth_response.json()['data']['access_token']
    print(f"✅ Token获取成功")
    
    # 测试创建问题
    print("\n📝 测试创建问题...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "question_text": "请介绍一下React的生命周期方法",
        "question_type": "technical",
        "difficulty": "medium", 
        "category": "前端开发",
        "answer_text": "React的生命周期方法包括：1. componentDidMount - 组件挂载后调用；2. componentDidUpdate - 组件更新后调用；3. componentWillUnmount - 组件卸载前调用。在函数组件中，可以使用useEffect Hook来实现类似的功能。",
        "tags": ["React", "生命周期", "前端"]
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(
        "http://localhost:5001/api/v1/questions/create",
        headers=headers,
        json=data
    )
    
    print(f"\n📊 响应状态码: {response.status_code}")
    print(f"📊 响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 问题创建成功!")
    else:
        print("❌ 问题创建失败!")

if __name__ == "__main__":
    test_create_question() 