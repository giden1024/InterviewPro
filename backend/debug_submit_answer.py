#!/usr/bin/env python3
"""
直接测试submit_answer功能
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置日志级别
logging.basicConfig(level=logging.INFO)

def test_submit_answer():
    """直接测试submit_answer功能"""
    print("🔍 测试submit_answer功能...")
    
    try:
        from app import create_app
        from app.services.interview_service import InterviewService
        
        app = create_app()
        with app.app_context():
            service = InterviewService()
            
            # 测试参数
            user_id = 12  # 从token中解析出的用户ID
            session_id = "55"  # 从API调用中获取的session_id
            question_id = 359  # 问题ID
            answer_text = "这是一个测试答案"
            response_time = 0
            
            print(f"参数: user_id={user_id}, session_id={session_id}, question_id={question_id}")
            
            # 调用submit_answer
            result = service.submit_answer(
                user_id=user_id,
                session_id=session_id,
                question_id=question_id,
                answer_text=answer_text,
                response_time=response_time
            )
            
            print(f"✅ 成功: {result}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_submit_answer() 