#!/usr/bin/env python3
"""
Celery异步任务配置
用于处理耗时的AI问题生成任务
"""
import os
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def make_celery(app):
    """创建Celery实例"""
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/2')
    )
    
    # 配置Celery
    celery.conf.update(
        # 任务序列化格式
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        
        # 任务路由
        task_routes={
            'app.tasks.question_tasks.generate_questions_async': {'queue': 'question_generation'},
            'app.tasks.question_tasks.generate_ai_reference_async': {'queue': 'ai_reference'},
        },
        
        # 任务执行配置
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        
        # 结果配置
        result_expires=3600,  # 1小时
        
        # 重试配置
        task_annotations={
            'app.tasks.question_tasks.generate_questions_async': {
                'rate_limit': '10/m',  # 每分钟最多10个任务
                'time_limit': 300,     # 5分钟超时
                'soft_time_limit': 240, # 4分钟软超时
                'retry_backoff': True,
                'max_retries': 3,
            },
            'app.tasks.question_tasks.generate_ai_reference_async': {
                'rate_limit': '30/m',  # 每分钟最多30个任务
                'time_limit': 60,      # 1分钟超时
                'soft_time_limit': 45, # 45秒软超时
                'retry_backoff': True,
                'max_retries': 2,
            }
        },
        
        # 监控配置
        worker_send_task_events=True,
        task_send_sent_event=True,
    )
    
    # 设置任务基类
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery 