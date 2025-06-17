#!/usr/bin/env python3
"""
WebSocket服务启动脚本
包含完整的WebSocket功能支持
"""

import os
import sys
from app import create_app
from app.extensions import socketio

def main():
    """启动WebSocket服务"""
    
    # 创建应用实例
    app = create_app()
    
    # 获取配置
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print("🚀 启动InterviewGenius WebSocket服务")
    print("=" * 50)
    print(f"📡 服务地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"🌐 WebSocket: 已启用")
    print(f"🔒 JWT认证: 已配置")
    print("=" * 50)
    
    try:
        # 启动SocketIO服务器
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            log_output=True
        )
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 