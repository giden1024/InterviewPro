#!/usr/bin/env python3
"""
修复循环导入问题
"""

import os

# 修复任务文件
tasks_content = '''#!/usr/bin/env python3
"""
问题生成异步任务
处理耗时的AI问题生成和AI参考答案生成
"""
import json
import logging
from celery import current_task
from celery.utils.log import get_task_logger
from datetime import datetime

from app.services.ai_question_generator import AIQuestionGenerator
from app.services.question_cache_service import QuestionCacheService
from app.models.resume import Resume
from app.models.question import InterviewType
from app.extensions import get_redis_client

logger = get_task_logger(__name__)

# 延迟导入Celery，避免循环导入
def get_celery_app():
    from app import create_app
    return create_app().celery

celery = get_celery_app()

@celery.task(bind=True)
def generate_questions_async(self, resume_data, user_id, interview_type, total_questions, 
                           difficulty_distribution=None, type_distribution=None):
    """
    异步生成面试问题
    
    Args:
        resume_data: 简历数据字典
        user_id: 用户ID
        interview_type: 面试类型
        total_questions: 问题总数
        difficulty_distribution: 难度分布
        type_distribution: 类型分布
    
    Returns:
        dict: 包含任务状态和结果
    """
    try:
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始生成问题...'
            }
        )
        
        # 创建简历对象
        resume = Resume(
            id=resume_data.get('id'),
            user_id=user_id,
            filename=resume_data.get('filename', ''),
            content=resume_data.get('content', ''),
            parsed_data=resume_data.get('parsed_data', {}),
            created_at=datetime.now()
        )
        
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 20,
                'total': 100,
                'status': '初始化AI生成器...'
            }
        )
        
        # 初始化AI生成器和缓存服务
        ai_generator = AIQuestionGenerator()
        cache_service = QuestionCacheService()
        
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 40,
                'total': 100,
                'status': '检查缓存...'
            }
        )
        
        # 检查缓存
        cached_questions = cache_service.get_cached_questions(
            user_id=user_id,
            resume=resume,
            interview_type=interview_type,
            total_questions=total_questions,
            difficulty_distribution=difficulty_distribution or {"easy": 2, "medium": 2, "hard": 1},
            type_distribution=type_distribution or {"technical": 3, "behavioral": 2}
        )
        
        if cached_questions:
            logger.info(f"✅ 用户{user_id}从缓存获取到 {len(cached_questions)} 个问题")
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': 100,
                    'total': 100,
                    'status': '从缓存获取问题完成'
                }
            )
            return {
                'status': 'SUCCESS',
                'questions': cached_questions,
                'from_cache': True,
                'generated_at': datetime.now().isoformat()
            }
        
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 60,
                'total': 100,
                'status': '调用AI生成问题...'
            }
        )
        
        # 生成问题
        questions = ai_generator.generate_questions_for_resume(
            resume=resume,
            user_id=user_id,
            interview_type=InterviewType(interview_type),
            total_questions=total_questions,
            difficulty_distribution=difficulty_distribution,
            type_distribution=type_distribution
        )
        
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 90,
                'total': 100,
                'status': '缓存生成的问题...'
            }
        )
        
        # 缓存问题
        cache_service.cache_questions(
            user_id=user_id,
            resume=resume,
            interview_type=interview_type,
            total_questions=total_questions,
            difficulty_distribution=difficulty_distribution or {"easy": 2, "medium": 2, "hard": 1},
            type_distribution=type_distribution or {"technical": 3, "behavioral": 2},
            questions=questions
        )
        
        # 完成
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 100,
                'total': 100,
                'status': '问题生成完成'
            }
        )
        
        logger.info(f"✅ 用户{user_id}异步生成完成 {len(questions)} 个问题")
        
        return {
            'status': 'SUCCESS',
            'questions': questions,
            'from_cache': False,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 异步问题生成失败: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e),
            'generated_at': datetime.now().isoformat()
        }

@celery.task(bind=True)
def generate_ai_reference_async(self, question_text, user_answer, job_title=None):
    """
    异步生成AI参考答案
    
    Args:
        question_text: 问题文本
        user_answer: 用户答案
        job_title: 职位标题
    
    Returns:
        dict: 包含AI参考答案
    """
    try:
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始生成AI参考答案...'
            }
        )
        
        # 初始化AI生成器
        ai_generator = AIQuestionGenerator()
        
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 50,
                'total': 100,
                'status': '调用AI生成参考答案...'
            }
        )
        
        # 生成AI参考答案
        ai_reference = ai_generator.generate_ai_reference_answer(
            question_text=question_text,
            user_answer=user_answer,
            job_title=job_title
        )
        
        # 完成
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 100,
                'total': 100,
                'status': 'AI参考答案生成完成'
            }
        )
        
        logger.info(f"✅ AI参考答案生成完成")
        
        return {
            'status': 'SUCCESS',
            'ai_reference': ai_reference,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ AI参考答案生成失败: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e),
            'generated_at': datetime.now().isoformat()
        }
'''

# 写入修复后的任务文件
with open('app/tasks/question_tasks.py', 'w', encoding='utf-8') as f:
    f.write(tasks_content)

print("✅ 已修复 question_tasks.py 的循环导入问题")

# 验证修复结果
print("🔍 验证修复结果...")
try:
    # 测试导入
    from app.api.questions import questions_bp
    print("✅ API文件导入成功")
    
    # 测试任务文件
    from app.tasks.question_tasks import generate_questions_async, generate_ai_reference_async
    print("✅ 任务文件导入成功")
    
    print("🎉 循环导入问题修复完成！")
    
except Exception as e:
    print(f"❌ 修复验证失败: {e}")
    import traceback
    traceback.print_exc()
