#!/usr/bin/env python3
"""
Celery Worker启动脚本
"""
from app import create_app

# 创建Flask应用
app = create_app()

# 获取Celery实例
celery = app.celery

if __name__ == '__main__':
    # 启动Celery worker
    celery.worker_main(['worker', '--loglevel=info', '--concurrency=1']) 