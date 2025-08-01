#!/usr/bin/env python3
"""
检查会话的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User
from app.models.question import InterviewSession, Question

def check_session_questions():
    """检查会话的问题"""
    app = create_app()
    
    with app.app_context():
        try:
            # 获取测试用户
            user = User.query.filter_by(email='test@example.com').first()
            if not user:
                print("❌ 测试用户不存在")
                return
            
            print(f"✅ 找到用户: {user.id}")
            
            # 获取用户的面试会话
            sessions = InterviewSession.query.filter_by(user_id=user.id).all()
            
            if not sessions:
                print("❌ 没有找到面试会话")
                return
            
            print(f"📋 检查 {len(sessions)} 个会话的问题:")
            
            for session in sessions:
                print(f"\n🔍 会话: {session.session_id}")
                print(f"   状态: {session.status}")
                
                # 获取会话的问题
                questions = Question.query.filter_by(session_id=session.id).all()
                print(f"   问题数量: {len(questions)}")
                
                if questions:
                    for i, q in enumerate(questions[:3]):  # 只显示前3个问题
                        print(f"     {i+1}. {q.question_text[:50]}...")
                    if len(questions) > 3:
                        print(f"     ... 还有 {len(questions) - 3} 个问题")
                else:
                    print("     ❌ 没有找到问题")
                
                print("    ---")
            
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_session_questions()
