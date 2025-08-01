#!/usr/bin/env python3
"""
直接测试问题详情API的修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_question_detail_directly():
    """直接测试问题详情API"""
    print("🔍 直接测试问题详情API...")
    
    try:
        from app import create_app
        from app.models.question import Question, Answer
        
        app = create_app()
        with app.app_context():
            # 获取问题337
            question = Question.query.get(337)
            if not question:
                print("❌ 问题337不存在")
                return
                
            print(f"✅ 找到问题337")
            print(f"   Session ID: {question.session_id}")
            print(f"   User ID: {question.user_id}")
            
            # 获取答案
            if question.session_id:
                answer = Answer.query.filter_by(
                    question_id=question.id,
                    user_id=question.user_id
                ).order_by(Answer.answered_at.desc()).first()
                
                print(f"   Found answer: {answer}")
                
                if answer:
                    latest_answer = {
                        'id': answer.id,
                        'answer_text': answer.answer_text,
                        'score': answer.score,
                        'answered_at': answer.answered_at.isoformat()
                    }
                    print(f"   Latest answer: {latest_answer}")
                else:
                    print("   No answer found")
            else:
                print("   No session_id")
                
            # 测试to_dict方法
            question_data = question.to_dict()
            print(f"   Question data keys: {list(question_data.keys())}")
            
            # 添加latest_answer
            question_data['latest_answer'] = latest_answer if 'latest_answer' in locals() else None
            print(f"   After adding latest_answer: {list(question_data.keys())}")
            
            # 测试返回结构
            from app.utils.response import success_response
            response_data = success_response(
                data={'question': question_data},
                message="Question details retrieved successfully"
            )
            
            print("✅ 测试完成")
            print(f"   Response structure: {response_data[0].json}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_question_detail_directly() 