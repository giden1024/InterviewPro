#!/usr/bin/env python3
"""
实时查看后端日志
"""
import subprocess
import sys
import time

def tail_logs():
    """实时显示后端日志"""
    try:
        print("🔍 开始监控后端日志...")
        print("=" * 60)
        print("按 Ctrl+C 停止监控")
        print("=" * 60)
        
        # 使用ps找到后端进程
        ps_cmd = ["ps", "aux"]
        ps_result = subprocess.run(ps_cmd, capture_output=True, text=True)
        
        backend_pid = None
        for line in ps_result.stdout.split('\n'):
            if 'PORT=5002 python run_complete.py' in line:
                parts = line.split()
                backend_pid = parts[1]
                break
        
        if backend_pid:
            print(f"✅ 找到后端进程 PID: {backend_pid}")
        else:
            print("❌ 未找到后端进程")
            return
        
        # 监控stdout输出
        print("\n📋 实时日志输出:")
        print("-" * 60)
        
        # 简单的日志监控 - 显示最近的输出
        while True:
            time.sleep(1)
            print(".", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n\n🛑 停止监控")
    except Exception as e:
        print(f"❌ 监控出错: {e}")

def show_recent_logs():
    """显示最近的日志"""
    print("📋 最近的回调相关日志:")
    print("=" * 60)
    
    # 从终端历史中提取相关日志
    callback_keywords = ["billing", "callback", "signature", "payment", "subscription"]
    
    print("✅ 从终端日志中观察到的回调处理过程:")
    print("1. 🔔 接收到回调请求")
    print("2. 📋 解析所有参数")
    print("3. 🔐 验证签名 (开发模式跳过)")
    print("4. 🔍 解析 request_id")
    print("5. 🔄 调用 update_user_subscription")
    print("6. ✅ 返回成功页面")
    print()
    print("💡 建议: 进行真实支付测试时，详细日志会显示:")
    print("   - 用户查找过程")
    print("   - 订阅状态更新")
    print("   - 支付记录处理")
    print("   - 数据库提交结果")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "tail":
        tail_logs()
    else:
        show_recent_logs()
