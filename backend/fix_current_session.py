#!/usr/bin/env python3
"""
修复当前会话的问题关联
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.question import Question, InterviewSession
from sqlalchemy import text

def fix_current_session():
    """修复当前会话的问题关联"""
    app = create_app()
    
    with app.app_context():
        try:
            # 当前会话ID和问题ID
            session_uuid = "b9496461-142e-4c3e-9aee-d7e3bdf7a1b0"
            
            print(f"🔧 修复会话: {session_uuid}")
            
            # 1. 查找会话
            session = InterviewSession.query.filter_by(session_id=session_uuid).first()
            if not session:
                print(f"❌ 会话不存在: {session_uuid}")
                return
            
            print(f"✅ 找到会话: ID={session.id}, 用户={session.user_id}")
            
            # 2. 查找用户的所有没有正确关联的问题
            # 通常是session_id为None或者不匹配的问题
            unassociated_questions = Question.query.filter(
                Question.user_id == session.user_id,
                Question.session_id != session.id
            ).order_by(Question.created_at.desc()).limit(10).all()
            
            print(f"📋 找到 {len(unassociated_questions)} 个需要关联的问题")
            
            # 3. 将最近的问题关联到当前会话
            fixed_count = 0
            for question in unassociated_questions:
                old_session_id = question.session_id
                question.session_id = session.id
                print(f"   问题 {question.id}: {old_session_id} -> {session.id}")
                fixed_count += 1
            
            # 4. 提交更改
            db.session.commit()
            print(f"✅ 成功修复 {fixed_count} 个问题的关联")
            
            # 5. 验证修复结果
            session_questions = Question.query.filter_by(
                session_id=session.id,
                user_id=session.user_id
            ).all()
            
            print(f"📊 会话现在包含 {len(session_questions)} 个问题")
            if session_questions:
                question_ids = [q.id for q in session_questions]
                print(f"   问题ID: {question_ids}")
                
        except Exception as e:
            print(f"❌ 修复过程中出错: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_current_session() 