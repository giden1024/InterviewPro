#!/usr/bin/env python3
"""
检查问题详情
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.question import Question, InterviewSession

def check_question_details():
    """检查问题详情"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查问题342
            question = Question.query.get(342)
            if question:
                print(f"问题342详情:")
                print(f"  ID: {question.id}")
                print(f"  用户ID: {question.user_id}")
                print(f"  会话ID: {question.session_id}")
                print(f"  简历ID: {question.resume_id}")
                print(f"  问题文本: {question.question_text[:100]}...")
                print(f"  问题类型: {question.question_type}")
                print(f"  难度: {question.difficulty}")
                print(f"  创建时间: {question.created_at}")
                print("---")
                
                # 检查关联的会话
                session = InterviewSession.query.get(question.session_id)
                if session:
                    print(f"关联会话详情:")
                    print(f"  会话ID: {session.session_id}")
                    print(f"  状态: {session.status}")
                    print(f"  用户ID: {session.user_id}")
                    print(f"  创建时间: {session.created_at}")
                    print(f"  开始时间: {session.started_at}")
                else:
                    print("❌ 没有找到关联的会话")
            else:
                print("❌ 没有找到问题342")
            
            print("\n" + "="*50 + "\n")
            
            # 检查问题337
            question = Question.query.get(337)
            if question:
                print(f"问题337详情:")
                print(f"  ID: {question.id}")
                print(f"  用户ID: {question.user_id}")
                print(f"  会话ID: {question.session_id}")
                print(f"  简历ID: {question.resume_id}")
                print(f"  问题文本: {question.question_text[:100]}...")
                print(f"  问题类型: {question.question_type}")
                print(f"  难度: {question.difficulty}")
                print(f"  创建时间: {question.created_at}")
                print("---")
                
                # 检查关联的会话
                session = InterviewSession.query.get(question.session_id)
                if session:
                    print(f"关联会话详情:")
                    print(f"  会话ID: {session.session_id}")
                    print(f"  状态: {session.status}")
                    print(f"  用户ID: {session.user_id}")
                    print(f"  创建时间: {session.created_at}")
                    print(f"  开始时间: {session.started_at}")
                else:
                    print("❌ 没有找到关联的会话")
            else:
                print("❌ 没有找到问题337")
            
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_question_details()
