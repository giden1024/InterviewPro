#!/usr/bin/env python3
import os
from app import create_app

# 创建应用实例
app = create_app()

@app.route('/health')
def health_check():
    """健康检查"""
    return {
        'status': 'healthy',
        'service': 'interview-genius-backend'
    }

if __name__ == '__main__':
    print("🚀 启动简化版后端服务...")
    print(f"🌐 访问地址: http://localhost:5001")
    
    # 简单启动，不使用SocketIO
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    ) 