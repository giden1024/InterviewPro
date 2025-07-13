#!/usr/bin/env python3
"""
修复现有问题的session_id关联
解决答案提交失败问题: "问题不存在、无权限访问或不属于当前面试会话"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question, InterviewSession
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_question_session_association():
    """修复问题与面试会话的关联"""
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 查询所有没有session_id的问题
            orphaned_questions = Question.query.filter(
                Question.session_id.is_(None)
            ).all()
            
            logger.info(f"发现 {len(orphaned_questions)} 个没有session_id关联的问题")
            
            if not orphaned_questions:
                logger.info("没有需要修复的问题")
                return
            
            # 2. 按user_id分组，尝试关联到对应的面试会话
            user_question_groups = {}
            for question in orphaned_questions:
                user_id = question.user_id
                if user_id not in user_question_groups:
                    user_question_groups[user_id] = []
                user_question_groups[user_id].append(question)
            
            fixed_count = 0
            
            for user_id, questions in user_question_groups.items():
                logger.info(f"处理用户 {user_id} 的 {len(questions)} 个问题")
                
                # 3. 获取该用户最近的面试会话
                recent_sessions = InterviewSession.query.filter_by(
                    user_id=user_id
                ).order_by(InterviewSession.created_at.desc()).limit(5).all()
                
                if not recent_sessions:
                    logger.warning(f"用户 {user_id} 没有面试会话，跳过")
                    continue
                
                # 4. 按时间顺序关联问题到会话
                for i, question in enumerate(questions):
                    # 优先关联到最近的会话
                    session_index = min(i // 10, len(recent_sessions) - 1)  # 每10个问题关联到一个会话
                    target_session = recent_sessions[session_index]
                    
                    # 更新问题的session_id
                    question.session_id = target_session.id
                    
                    logger.info(f"问题 {question.id} 关联到会话 {target_session.session_id}")
                    fixed_count += 1
            
            # 5. 提交更改
            db.session.commit()
            
            logger.info(f"成功修复 {fixed_count} 个问题的session_id关联")
            
            # 6. 验证修复结果
            remaining_orphaned = Question.query.filter(
                Question.session_id.is_(None)
            ).count()
            
            logger.info(f"修复后仍有 {remaining_orphaned} 个问题没有session_id关联")
            
            # 7. 显示特定问题的修复状态
            specific_question = Question.query.filter_by(id=1021).first()
            if specific_question:
                logger.info(f"问题 1021 的session_id: {specific_question.session_id}")
                if specific_question.session_id:
                    session = InterviewSession.query.get(specific_question.session_id)
                    if session:
                        logger.info(f"问题 1021 关联到会话: {session.session_id}")
                    else:
                        logger.error(f"问题 1021 的session_id {specific_question.session_id} 无效")
            
        except Exception as e:
            logger.error(f"修复过程中出错: {e}")
            db.session.rollback()
            raise

def show_question_session_stats():
    """显示问题与会话关联的统计信息"""
    app = create_app()
    
    with app.app_context():
        try:
            # 统计信息
            total_questions = Question.query.count()
            questions_with_session = Question.query.filter(
                Question.session_id.is_not(None)
            ).count()
            questions_without_session = total_questions - questions_with_session
            
            logger.info("=== 问题与会话关联统计 ===")
            logger.info(f"总问题数: {total_questions}")
            logger.info(f"已关联会话: {questions_with_session}")
            logger.info(f"未关联会话: {questions_without_session}")
            
            # 用户统计
            users_with_questions = db.session.query(
                Question.user_id,
                db.func.count(Question.id).label('question_count'),
                db.func.sum(db.case([(Question.session_id.is_(None), 1)], else_=0)).label('orphaned_count')
            ).group_by(Question.user_id).all()
            
            logger.info("=== 用户问题统计 ===")
            for user_id, question_count, orphaned_count in users_with_questions:
                logger.info(f"用户 {user_id}: {question_count} 个问题, {orphaned_count} 个未关联")
            
        except Exception as e:
            logger.error(f"统计过程中出错: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stats':
        show_question_session_stats()
    else:
        print("🔧 开始修复问题与会话的关联...")
        fix_question_session_association()
        print("✅ 修复完成！")
        print("📊 显示统计信息...")
        show_question_session_stats() 