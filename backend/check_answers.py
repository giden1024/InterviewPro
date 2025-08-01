#!/usr/bin/env python3
"""
检查答案
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.question import Answer

def check_answers():
    """检查答案"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查问题342的答案
            answers = Answer.query.filter_by(question_id=342).all()
            print(f"问题342的答案数量: {len(answers)}")
            
            for answer in answers:
                print(f"答案ID: {answer.id}")
                print(f"会话ID: {answer.session_id}")
                print(f"用户ID: {answer.user_id}")
                print(f"答案文本: {answer.answer_text}")
                print(f"回答时间: {answer.answered_at}")
                print("---")
            
            # 检查问题337的答案
            answers = Answer.query.filter_by(question_id=337).all()
            print(f"问题337的答案数量: {len(answers)}")
            
            for answer in answers:
                print(f"答案ID: {answer.id}")
                print(f"会话ID: {answer.session_id}")
                print(f"用户ID: {answer.user_id}")
                print(f"答案文本: {answer.answer_text}")
                print(f"回答时间: {answer.answered_at}")
                print("---")
            
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_answers()
