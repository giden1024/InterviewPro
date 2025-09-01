#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.app.models.question import QuestionType, QuestionDifficulty
from backend.app.services.ai_question_generator import AIQuestionGenerator

def test_enum_fix():
    """测试枚举值修复"""
    
    app = create_app()
    
    with app.app_context():
        # 创建AI问题生成器实例
        generator = AIQuestionGenerator()
        
        print("🔍 测试fallback问题生成...")
        
        # 测试fallback问题生成
        questions = generator._get_fallback_questions_batch(
            QuestionType.TECHNICAL,
            QuestionDifficulty.MEDIUM,
            2
        )
        
        print(f"📝 生成的问题数量: {len(questions)}")
        
        if questions:
            first_q = questions[0]
            print(f"🔍 第一个问题详情:")
            print(f"  - 问题文本: {first_q['question_text']}")
            print(f"  - 问题类型: {first_q['question_type']} (类型: {type(first_q['question_type'])})")
            print(f"  - 难度: {first_q['difficulty']} (类型: {type(first_q['difficulty'])})")
            
            # 验证是否为字符串
            if isinstance(first_q['question_type'], str) and isinstance(first_q['difficulty'], str):
                print("✅ 枚举值修复成功！返回的是字符串值")
            else:
                print("❌ 枚举值修复失败！返回的不是字符串值")

if __name__ == "__main__":
    test_enum_fix() 