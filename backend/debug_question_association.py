#!/usr/bin/env python3
"""
调试问题1021的session关联情况
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question, InterviewSession

def debug_question_1021():
    """调试问题1021的关联情况"""
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 查找问题1021
            question = Question.query.filter_by(id=1021).first()
            if not question:
                print("❌ 问题1021不存在")
                return
            
            print(f"✅ 问题1021存在")
            print(f"   - 用户ID: {question.user_id}")
            print(f"   - Session ID: {question.session_id}")
            print(f"   - 问题文本: {question.question_text[:100]}...")
            
            # 2. 查找对应的会话
            if question.session_id:
                session = InterviewSession.query.get(question.session_id)
                if session:
                    print(f"✅ 找到对应会话:")
                    print(f"   - 会话数据库ID: {session.id}")
                    print(f"   - 会话UUID: {session.session_id}")
                    print(f"   - 会话标题: {session.title}")
                    print(f"   - 会话状态: {session.status}")
                else:
                    print(f"❌ 会话ID {question.session_id} 不存在")
            else:
                print("❌ 问题1021没有关联session_id")
            
            # 3. 查找用户的所有会话
            print(f"\n📋 用户 {question.user_id} 的所有会话:")
            user_sessions = InterviewSession.query.filter_by(
                user_id=question.user_id
            ).order_by(InterviewSession.created_at.desc()).all()
            
            for i, s in enumerate(user_sessions):
                print(f"   {i+1}. {s.session_id} - {s.title} - {s.status}")
            
            # 4. 验证特定会话的问题
            target_session_uuid = "696a0437-ee96-425d-a01a-79355683d1b0"
            target_session = InterviewSession.query.filter_by(
                session_id=target_session_uuid
            ).first()
            
            if target_session:
                print(f"\n🎯 目标会话 {target_session_uuid}:")
                print(f"   - 数据库ID: {target_session.id}")
                print(f"   - 标题: {target_session.title}")
                print(f"   - 状态: {target_session.status}")
                
                # 查找这个会话的所有问题
                session_questions = Question.query.filter_by(
                    session_id=target_session.id
                ).all()
                print(f"   - 包含问题数量: {len(session_questions)}")
                
                if session_questions:
                    print("   - 问题ID范围:", 
                          f"{min(q.id for q in session_questions)} - {max(q.id for q in session_questions)}")
                    if any(q.id == 1021 for q in session_questions):
                        print("   ✅ 包含问题1021")
                    else:
                        print("   ❌ 不包含问题1021")
                
            else:
                print(f"\n❌ 目标会话 {target_session_uuid} 不存在")
                
            # 5. 测试查询逻辑
            print(f"\n🔍 测试查询逻辑:")
            if question.session_id and target_session:
                test_question = Question.query.filter_by(
                    id=1021,
                    user_id=question.user_id,
                    session_id=target_session.id
                ).first()
                
                if test_question:
                    print("   ✅ 查询逻辑匹配成功")
                else:
                    print("   ❌ 查询逻辑失败")
                    print(f"   - 查询条件: id=1021, user_id={question.user_id}, session_id={target_session.id}")
                    print(f"   - 实际数据: id=1021, user_id={question.user_id}, session_id={question.session_id}")
                    
        except Exception as e:
            print(f"❌ 调试过程中出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_question_1021() 