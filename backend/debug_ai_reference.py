#!/usr/bin/env python3
"""
AI参考答案生成调试脚本
详细诊断AI参考答案生成过程中的问题
"""

import sys
import os
import time
import json
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_ai_reference_generation():
    """调试AI参考答案生成过程"""
    print("🔍 开始调试AI参考答案生成...")
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.services.ai_question_generator import AIQuestionGenerator
            from app.models.question import Question
            from app.models.resume import Resume
            from app.extensions import db
            
            # 初始化AI生成器
            generator = AIQuestionGenerator()
            
            # 获取测试数据
            test_question = db.session.query(Question).first()
            test_resume = db.session.query(Resume).first()
            
            if not test_question or not test_resume:
                print("❌ 未找到测试数据")
                return
            
            print(f"📋 测试问题: {test_question.question_text[:50]}...")
            print(f"📄 测试简历: {test_resume.original_filename}")
            
            # 步骤1: 检查AI客户端
            print("\n🔍 步骤1: 检查AI客户端...")
            client = generator._get_client()
            if client:
                print("✅ AI客户端初始化成功")
                print(f"🤖 模型: {generator.model}")
            else:
                print("❌ AI客户端初始化失败")
                return
            
            # 步骤2: 准备简历上下文
            print("\n🔍 步骤2: 准备简历上下文...")
            try:
                resume_context = generator._prepare_resume_context_optimized(test_resume)
                print("✅ 简历上下文准备成功")
                print(f"📊 上下文数据: {json.dumps(resume_context, ensure_ascii=False, indent=2)}")
            except Exception as e:
                print(f"❌ 简历上下文准备失败: {e}")
                traceback.print_exc()
                return
            
            # 步骤3: 构建提示
            print("\n🔍 步骤3: 构建提示...")
            try:
                prompt = generator._build_reference_answer_prompt_optimized(
                    question=test_question,
                    resume_context=resume_context,
                    user_context={}
                )
                print("✅ 提示构建成功")
                print(f"📝 提示长度: {len(prompt)} 字符")
                print(f"📋 提示内容: {prompt[:200]}...")
            except Exception as e:
                print(f"❌ 提示构建失败: {e}")
                traceback.print_exc()
                return
            
            # 步骤4: 获取系统提示
            print("\n🔍 步骤4: 获取系统提示...")
            try:
                system_prompt = generator._get_reference_answer_system_prompt_optimized()
                print("✅ 系统提示获取成功")
                print(f"📝 系统提示长度: {len(system_prompt)} 字符")
                print(f"📋 系统提示内容: {system_prompt}")
            except Exception as e:
                print(f"❌ 系统提示获取失败: {e}")
                traceback.print_exc()
                return
            
            # 步骤5: 调用AI API
            print("\n🔍 步骤5: 调用AI API...")
            try:
                start_time = time.time()
                
                response = client.chat.completions.create(
                    model=generator.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.2,
                    timeout=25,
                    presence_penalty=0.0,
                    frequency_penalty=0.0,
                    top_p=0.9,
                    stream=False
                )
                
                end_time = time.time()
                api_time = end_time - start_time
                
                print(f"✅ AI API调用成功!")
                print(f"⏱️  API调用时间: {api_time:.2f} 秒")
                
                # 检查响应
                if not response:
                    print("❌ AI响应为空")
                    return
                
                print(f"📊 响应对象类型: {type(response)}")
                print(f"📊 响应属性: {dir(response)}")
                
                if not hasattr(response, 'choices'):
                    print("❌ 响应没有choices属性")
                    return
                
                print(f"📊 choices数量: {len(response.choices)}")
                
                if len(response.choices) == 0:
                    print("❌ choices为空")
                    return
                
                choice = response.choices[0]
                print(f"📊 choice类型: {type(choice)}")
                print(f"📊 choice属性: {dir(choice)}")
                
                if not hasattr(choice, 'message'):
                    print("❌ choice没有message属性")
                    return
                
                message = choice.message
                print(f"📊 message类型: {type(message)}")
                print(f"📊 message属性: {dir(message)}")
                
                if not hasattr(message, 'content'):
                    print("❌ message没有content属性")
                    return
                
                content = message.content
                print(f"✅ 获取到AI响应内容!")
                print(f"📝 内容长度: {len(content)} 字符")
                print(f"📋 内容预览: {content[:200]}...")
                
            except Exception as e:
                print(f"❌ AI API调用失败: {e}")
                traceback.print_exc()
                return
            
            # 步骤6: 解析响应
            print("\n🔍 步骤6: 解析响应...")
            try:
                result = generator._parse_reference_answer_response(content, test_question)
                print("✅ 响应解析成功")
                print(f"🤖 生成方式: {result.get('generated_by', 'unknown')}")
                
                if 'sample_answer' in result:
                    sample_answer = result['sample_answer']
                    print(f"📝 参考答案长度: {len(sample_answer)} 字符")
                    print(f"📋 参考答案预览: {sample_answer[:100]}...")
                
            except Exception as e:
                print(f"❌ 响应解析失败: {e}")
                traceback.print_exc()
                return
            
            print("\n🎉 调试完成! AI参考答案生成流程正常")
            
        except Exception as e:
            print(f"❌ 调试过程中出现错误: {e}")
            traceback.print_exc()

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 AI参考答案生成调试")
    print("=" * 60)
    
    debug_ai_reference_generation()
    
    print("\n" + "=" * 60)
    print("✅ 调试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main() 