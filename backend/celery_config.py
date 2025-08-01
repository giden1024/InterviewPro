#!/usr/bin/env python3
"""
Celery配置文件
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

# 注册任务
from app.tasks.question_tasks import generate_questions_async, generate_ai_reference_async

# 将函数注册为Celery任务，使用正确的任务名称
generate_questions_task = celery.task(name='app.tasks.question_tasks.generate_questions_async')(generate_questions_async)
generate_ai_reference_task = celery.task(name='app.tasks.question_tasks.generate_ai_reference_async')(generate_ai_reference_async)

if __name__ == '__main__':
    print("🚀 启动Celery Worker...")
    print(f"Celery应用: {celery}")
    print(f"Broker: {celery.conf.broker_url}")
    print(f"Backend: {celery.conf.result_backend}")
    
    # 启动worker
    celery.worker_main(['worker', '--loglevel=info', '--concurrency=1']) 