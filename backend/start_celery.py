#!/usr/bin/env python3
"""
简单的Celery Worker启动脚本
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# 创建Flask应用
app = create_app()

# 获取Celery实例
celery = app.celery

# 确保导入任务模块
import app.tasks.question_tasks

if __name__ == '__main__':
    print("🚀 启动Celery Worker...")
    print(f"Celery应用: {celery}")
    print(f"Broker: {celery.conf.broker_url}")
    print(f"Backend: {celery.conf.result_backend}")
    
    # 启动worker
    celery.worker_main(['worker', '--loglevel=info', '--concurrency=1']) 