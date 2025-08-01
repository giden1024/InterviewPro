#!/usr/bin/env python3
"""
检查会话状态
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User
from app.models.question import InterviewSession

def check_session_status():
    """检查会话状态"""
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
            
            print(f"📋 找到 {len(sessions)} 个会话:")
            
            for session in sessions:
                print(f"  - 会话ID: {session.session_id}")
                print(f"    状态: {session.status}")
                print(f"    创建时间: {session.created_at}")
                print(f"    开始时间: {session.started_at}")
                print(f"    完成时间: {session.completed_at}")
                print(f"    总问题数: {session.total_questions}")
                print(f"    已完成问题数: {session.completed_questions}")
                print("    ---")
            
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_session_status()
