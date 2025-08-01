#!/usr/bin/env python3
"""
Celery Worker启动脚本
用于启动异步任务处理worker
"""
import os
import sys
from celery import Celery
from app import create_app

def start_celery_worker():
    """启动Celery Worker"""
    print("🚀 启动Celery Worker...")
    
    # 创建Flask应用
    app = create_app()
    
    # 获取Celery实例
    celery = app.celery
    
    # 启动worker
    celery.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2',  # 并发worker数量
        '--queues=question_generation,ai_reference',  # 指定队列
        '--hostname=worker1@%h'  # worker主机名
    ])

if __name__ == '__main__':
    start_celery_worker() 