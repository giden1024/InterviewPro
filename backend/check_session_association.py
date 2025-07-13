#!/usr/bin/env python3
"""
检查会话和问题的关联状况
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.question import Question, InterviewSession
from sqlalchemy import text

def check_session_association():
    """检查会话和问题的关联状况"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查当前的会话ID
            session_uuid = "b9496461-142e-4c3e-9aee-d7e3bdf7a1b0"
            question_id = 1167
            
            print(f"🔍 检查会话: {session_uuid}")
            print(f"🔍 检查问题: {question_id}")
            
            # 1. 查找会话
            session = InterviewSession.query.filter_by(session_id=session_uuid).first()
            if session:
                print(f"✅ 找到会话:")
                print(f"   - 数据库ID: {session.id}")
                print(f"   - 用户ID: {session.user_id}")
                print(f"   - 标题: {session.title}")
                print(f"   - 状态: {session.status}")
            else:
                print(f"❌ 会话不存在: {session_uuid}")
                return
            
            # 2. 查找问题
            question = Question.query.filter_by(id=question_id).first()
            if question:
                print(f"✅ 找到问题:")
                print(f"   - 问题ID: {question.id}")
                print(f"   - 用户ID: {question.user_id}")
                print(f"   - Session ID: {question.session_id}")
                print(f"   - 问题文本: {question.question_text[:100]}...")
            else:
                print(f"❌ 问题不存在: {question_id}")
                return
            
            # 3. 检查关联
            print(f"\n🔍 检查关联:")
            print(f"   - 问题的session_id: {question.session_id}")
            print(f"   - 会话的数据库ID: {session.id}")
            print(f"   - 用户ID匹配: {question.user_id == session.user_id}")
            print(f"   - Session ID匹配: {question.session_id == session.id}")
            
            # 4. 模拟API查询
            print(f"\n🧪 模拟API查询:")
            test_question = Question.query.filter_by(
                id=question_id,
                user_id=session.user_id,
                session_id=session.id
            ).first()
            
            if test_question:
                print("   ✅ API查询会成功")
            else:
                print("   ❌ API查询会失败")
                print(f"   - 查询条件: id={question_id}, user_id={session.user_id}, session_id={session.id}")
                print(f"   - 实际数据: id={question.id}, user_id={question.user_id}, session_id={question.session_id}")
            
            # 5. 查看这个会话的所有问题
            print(f"\n📋 会话 {session_uuid} 的所有问题:")
            session_questions = Question.query.filter_by(session_id=session.id).all()
            print(f"   - 总数: {len(session_questions)}")
            if session_questions:
                question_ids = [q.id for q in session_questions]
                print(f"   - 问题ID范围: {min(question_ids)} - {max(question_ids)}")
                if question_id in question_ids:
                    print(f"   ✅ 包含问题 {question_id}")
                else:
                    print(f"   ❌ 不包含问题 {question_id}")
            
            # 6. 查看问题1167属于哪个会话
            if question.session_id:
                actual_session = InterviewSession.query.get(question.session_id)
                if actual_session:
                    print(f"\n📋 问题 {question_id} 实际属于会话:")
                    print(f"   - 会话UUID: {actual_session.session_id}")
                    print(f"   - 会话标题: {actual_session.title}")
                    print(f"   - 会话状态: {actual_session.status}")
                else:
                    print(f"\n❌ 问题 {question_id} 的session_id {question.session_id} 无效")
            else:
                print(f"\n❌ 问题 {question_id} 没有session_id")
                
        except Exception as e:
            print(f"❌ 检查过程中出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_session_association() 