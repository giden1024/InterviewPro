#!/usr/bin/env python3
"""
快速测试AI参考答案生成优化效果
"""

import sys
import os
import time
import requests
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_reference_generation():
    """测试AI参考答案生成性能"""
    print("🚀 快速测试AI参考答案生成优化效果...")
    
    # 测试URL
    url = "http://localhost:5001/api/v1/questions/352/generate-reference"
    
    # 设置请求头（模拟前端请求）
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-test-token'  # 需要有效的token
    }
    
    print(f"📡 测试URL: {url}")
    print(f"⏰ 开始时间: {time.strftime('%H:%M:%S')}")
    
    try:
        # 发送请求并计时
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=60)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"✅ 请求完成!")
        print(f"⏱️  响应时间: {response_time:.2f} 秒")
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 请求成功!")
            data = response.json()
            print(f"📝 响应数据长度: {len(json.dumps(data))} 字符")
        else:
            print(f"⚠️  请求失败: {response.text}")
            
        # 性能评估
        if response_time < 20:
            print("🎉 性能优秀! 响应时间 < 20秒")
        elif response_time < 30:
            print("✅ 性能良好! 响应时间 < 30秒")
        elif response_time < 40:
            print("⚠️  性能一般! 响应时间 < 40秒")
        else:
            print("❌ 性能需要优化! 响应时间 > 40秒")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时 (60秒)")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，请检查后端服务是否运行")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def check_backend_status():
    """检查后端服务状态"""
    print("🔍 检查后端服务状态...")
    
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"⚠️  后端服务状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端服务连接失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🤖 AI参考答案生成快速测试")
    print("=" * 50)
    
    # 检查后端服务状态
    if not check_backend_status():
        print("❌ 后端服务未运行，请先启动后端服务")
        return
    
    # 测试AI参考答案生成
    test_ai_reference_generation()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    main() 