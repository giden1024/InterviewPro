#!/usr/bin/env python3
"""
AI问题生成功能演示脚本
展示基于简历信息生成个性化面试问题的核心功能
"""

import json
import sys
import os
from datetime import datetime

# 模拟简历数据（基于之前解析的app_cv.pdf）
SAMPLE_RESUME = {
    "name": "ZHENGHAN FANG",
    "email": "zbf5037@psu.edu",
    "phone": "(814) 777-5136",
    "skills": [
        "Python", "Java", "JavaScript", "React", "Node.js",
        "SQL", "MongoDB", "AWS", "Docker", "Git",
        "Machine Learning", "Data Analysis", "API Development",
        "Web Development", "Database Design", "System Architecture",
        "Agile", "Scrum", "CI/CD", "Testing", "Linux"
    ],
    "experience": [
        {
            "title": "Software Engineer",
            "company": "Tech Company",
            "duration": "2022-2024",
            "description": "Developed web applications using React and Node.js"
        },
        {
            "title": "Data Analyst Intern",
            "company": "Data Corp",
            "duration": "2021-2022",
            "description": "Analyzed data using Python and SQL"
        }
    ],
    "education": [
        {
            "degree": "Master of Science",
            "field": "Computer Science",
            "school": "Pennsylvania State University",
            "year": "2024"
        }
    ]
}

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_section(title):
    """打印章节"""
    print(f"\n📋 {title}")
    print("-" * 40)

def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")

def print_info(message):
    """打印信息"""
    print(f"ℹ️  {message}")

def generate_mock_questions(resume_data, interview_type="comprehensive", total_questions=10):
    """
    模拟AI问题生成逻辑
    展示如何基于简历信息生成个性化问题
    """
    questions = []
    
    # 根据面试类型确定问题分布
    if interview_type == "technical":
        type_distribution = {"technical": 6, "experience": 2, "situational": 2}
    elif interview_type == "hr":
        type_distribution = {"behavioral": 4, "experience": 3, "situational": 2, "general": 1}
    else:  # comprehensive
        type_distribution = {"technical": 3, "behavioral": 3, "experience": 2, "situational": 2}
    
    # 难度分布
    difficulty_distribution = {"easy": 3, "medium": 5, "hard": 2}
    
    # 生成问题
    question_id = 1
    
    # 技术问题
    if "technical" in type_distribution:
        for i in range(type_distribution["technical"]):
            skill = resume_data["skills"][i % len(resume_data["skills"])]
            difficulty = "easy" if i < 2 else "medium" if i < 4 else "hard"
            
            if skill in ["Python", "JavaScript", "Java"]:
                if difficulty == "easy":
                    question_text = f"请简单介绍一下{skill}语言的主要特点和优势。"
                elif difficulty == "medium":
                    question_text = f"请描述您在{skill}项目中遇到的一个技术挑战以及解决方案。"
                else:
                    question_text = f"如何设计一个高性能的{skill}应用架构？请详细说明。"
            elif skill in ["React", "Node.js"]:
                if difficulty == "easy":
                    question_text = f"请解释{skill}的核心概念和工作原理。"
                else:
                    question_text = f"在{skill}开发中，如何优化性能和处理大量并发请求？"
            else:
                question_text = f"请分享您使用{skill}的实际经验和最佳实践。"
            
            questions.append({
                "id": question_id,
                "question_text": question_text,
                "question_type": "technical",
                "difficulty": difficulty,
                "category": skill,
                "tags": [skill, "编程", "技术"],
                "expected_answer": f"应该包含{skill}的核心概念、实际应用经验等",
                "evaluation_criteria": {
                    "technical_accuracy": "技术理解的准确性",
                    "practical_experience": "实际项目经验",
                    "problem_solving": "解决问题的能力"
                }
            })
            question_id += 1
    
    # 行为问题
    if "behavioral" in type_distribution:
        behavioral_questions = [
            {
                "text": "请描述一次您在团队项目中遇到分歧时是如何处理的？",
                "category": "团队协作",
                "tags": ["团队合作", "沟通", "冲突解决"]
            },
            {
                "text": "请分享一个您主动学习新技术并应用到项目中的经历。",
                "category": "学习能力",
                "tags": ["学习能力", "主动性", "技术成长"]
            },
            {
                "text": "当您面临紧急的项目deadline时，您是如何管理时间和优先级的？",
                "category": "时间管理",
                "tags": ["时间管理", "压力处理", "优先级"]
            }
        ]
        
        for i in range(type_distribution["behavioral"]):
            q = behavioral_questions[i % len(behavioral_questions)]
            difficulty = "easy" if i < 1 else "medium"
            
            questions.append({
                "id": question_id,
                "question_text": q["text"],
                "question_type": "behavioral",
                "difficulty": difficulty,
                "category": q["category"],
                "tags": q["tags"],
                "expected_answer": "应该包含具体的情况描述、采取的行动和结果",
                "evaluation_criteria": {
                    "situation_clarity": "情况描述的清晰度",
                    "action_effectiveness": "采取行动的有效性",
                    "learning_reflection": "反思和学习能力"
                }
            })
            question_id += 1
    
    # 经验问题
    if "experience" in type_distribution:
        for i in range(type_distribution["experience"]):
            if i == 0:
                question_text = "请详细介绍您最引以为豪的项目，包括您的角色、技术栈和取得的成果。"
                category = "项目经验"
            else:
                question_text = "在您的工作经历中，哪个项目让您学到最多？为什么？"
                category = "学习成长"
            
            questions.append({
                "id": question_id,
                "question_text": question_text,
                "question_type": "experience",
                "difficulty": "medium",
                "category": category,
                "tags": ["项目经验", "成长", "成就"],
                "expected_answer": "应该包含项目背景、个人贡献、技术难点、成果等",
                "evaluation_criteria": {
                    "project_complexity": "项目复杂度",
                    "personal_contribution": "个人贡献度",
                    "technical_depth": "技术深度"
                }
            })
            question_id += 1
    
    # 情景问题
    if "situational" in type_distribution:
        situational_questions = [
            "假如您需要在两个月内开发一个新的Web应用，但只有一个初级开发者协助您，您会如何规划和执行？",
            "如果您发现生产环境中有一个严重的性能问题，影响用户体验，您会采取什么步骤来解决？"
        ]
        
        for i in range(type_distribution["situational"]):
            questions.append({
                "id": question_id,
                "question_text": situational_questions[i % len(situational_questions)],
                "question_type": "situational",
                "difficulty": "medium",
                "category": "问题解决",
                "tags": ["情景分析", "解决方案", "决策"],
                "expected_answer": "应该包含分析思路、解决步骤、预期结果等",
                "evaluation_criteria": {
                    "analytical_thinking": "分析思维能力",
                    "solution_feasibility": "解决方案可行性",
                    "risk_consideration": "风险考虑"
                }
            })
            question_id += 1
    
    # 通用问题
    if "general" in type_distribution:
        questions.append({
            "id": question_id,
            "question_text": "请介绍一下您的职业目标，以及为什么选择我们公司？",
            "question_type": "general",
            "difficulty": "easy",
            "category": "职业规划",
            "tags": ["职业规划", "动机", "公司了解"],
            "expected_answer": "应该包含明确的职业目标和对公司的了解",
            "evaluation_criteria": {
                "goal_clarity": "目标明确性",
                "company_research": "公司了解程度",
                "motivation": "动机真实性"
            }
        })
    
    return questions[:total_questions]

def simulate_interview_session(resume_data, interview_type="comprehensive"):
    """模拟完整的面试会话过程"""
    print_header(f"AI面试问题生成演示 - {interview_type.upper()}面试")
    
    # 1. 简历信息分析
    print_section("1. 简历信息分析")
    print_info(f"候选人姓名: {resume_data['name']}")
    print_info(f"主要技能: {', '.join(resume_data['skills'][:8])}...")
    print_info(f"工作经验: {len(resume_data['experience'])}项")
    print_info(f"教育背景: {len(resume_data['education'])}项")
    
    # 2. 面试类型和配置
    print_section("2. 面试配置")
    type_configs = {
        "technical": "技术面试 - 主要考察编程和技术能力",
        "hr": "HR面试 - 主要考察行为和软技能",
        "comprehensive": "综合面试 - 技术和行为并重"
    }
    print_info(f"面试类型: {type_configs[interview_type]}")
    print_info("问题总数: 10")
    print_info("难度分布: 简单(3) + 中等(5) + 困难(2)")
    
    # 3. AI问题生成
    print_section("3. AI问题生成")
    print_info("正在基于简历信息生成个性化问题...")
    
    questions = generate_mock_questions(resume_data, interview_type, 10)
    print_success(f"成功生成 {len(questions)} 个问题")
    
    # 4. 问题展示
    print_section("4. 生成的问题列表")
    
    # 按类型分组展示
    question_by_type = {}
    for q in questions:
        q_type = q["question_type"]
        if q_type not in question_by_type:
            question_by_type[q_type] = []
        question_by_type[q_type].append(q)
    
    type_labels = {
        "technical": "🔧 技术问题",
        "behavioral": "👥 行为问题", 
        "experience": "💼 经验问题",
        "situational": "🎯 情景问题",
        "general": "📝 通用问题"
    }
    
    for q_type, type_questions in question_by_type.items():
        print(f"\n{type_labels.get(q_type, q_type.upper())} ({len(type_questions)}个):")
        for i, q in enumerate(type_questions, 1):
            print(f"  {i}. [{q['difficulty'].upper()}] {q['question_text']}")
            print(f"     分类: {q['category']} | 标签: {', '.join(q['tags'])}")
            print(f"     期望答案: {q['expected_answer']}")
            print()
    
    # 5. 面试流程模拟
    print_section("5. 面试流程模拟")
    print_info("模拟面试开始...")
    
    # 展示前3个问题的详细信息
    for i in range(min(3, len(questions))):
        q = questions[i]
        print(f"\n📝 问题 {i+1}/{len(questions)} [{q['question_type']}/{q['difficulty']}]")
        print(f"   {q['question_text']}")
        print(f"   💡 评估标准:")
        for criterion, description in q['evaluation_criteria'].items():
            print(f"      • {description}")
        
        # 模拟用户回答
        sample_answers = [
            "我认为这个问题很有挑战性。基于我的经验...",
            "在我之前的项目中，我遇到过类似的情况...",
            "这需要从多个角度来考虑..."
        ]
        print(f"   💬 模拟答案: {sample_answers[i]}")
        print(f"   ⏱️  回答用时: {60 + i*20}秒")
        print(f"   ✅ 答案已提交")
    
    print_info(f"模拟回答了前3个问题，剩余{len(questions)-3}个问题...")
    
    # 6. 统计信息
    print_section("6. 面试统计")
    
    difficulty_count = {}
    type_count = {}
    
    for q in questions:
        # 统计难度分布
        diff = q['difficulty']
        difficulty_count[diff] = difficulty_count.get(diff, 0) + 1
        
        # 统计类型分布
        q_type = q['question_type']
        type_count[q_type] = type_count.get(q_type, 0) + 1
    
    print("📊 问题分布统计:")
    print("   难度分布:")
    for diff, count in difficulty_count.items():
        print(f"     • {diff}: {count}个")
    
    print("   类型分布:")
    for q_type, count in type_count.items():
        print(f"     • {q_type}: {count}个")
    
    print(f"\n📈 面试质量评估:")
    print(f"   • 个性化程度: 高 (基于{len(resume_data['skills'])}项技能)")
    print(f"   • 难度层次: 均衡 (3个难度级别)")
    print(f"   • 覆盖面: 全面 ({len(type_count)}种问题类型)")
    print(f"   • 实用性: 强 (结合实际工作场景)")

def main():
    """主演示流程"""
    print("🤖 InterviewGenius AI - 智能面试问题生成演示")
    print(f"⏰ 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 演示不同类型的面试
    interview_types = [
        ("comprehensive", "综合面试"),
        ("technical", "技术面试"), 
        ("hr", "HR面试")
    ]
    
    for interview_type, type_name in interview_types:
        simulate_interview_session(SAMPLE_RESUME, interview_type)
        
        if interview_type != interview_types[-1][0]:
            input(f"\n按Enter键继续演示下一种面试类型 ({interview_types[interview_types.index((interview_type, type_name))+1][1]})...")
    
    print_header("演示总结")
    print("🎉 AI面试问题生成功能演示完成！")
    print("\n🌟 核心特性:")
    print("   ✅ 基于简历技能自动生成个性化问题")
    print("   ✅ 支持多种面试类型和难度级别")
    print("   ✅ 包含期望答案和评估标准")
    print("   ✅ 智能分配问题类型和难度分布")
    print("   ✅ 完整的面试流程管理")
    
    print("\n💡 技术亮点:")
    print("   🔧 AI驱动的问题生成算法")
    print("   📊 智能的难度和类型平衡")
    print("   🎯 基于简历的个性化定制")
    print("   📝 结构化的评估标准")
    print("   🔄 完整的面试会话管理")
    
    print("\n🚀 应用价值:")
    print("   • 大幅提升面试准备效率")
    print("   • 提供个性化的面试体验")
    print("   • 帮助求职者发现技能盲点")
    print("   • 支持不同类型的面试需求")
    
    print(f"\n{'='*60}")
    print("💼 InterviewGenius AI - 让面试更智能，让求职更成功！")

if __name__ == "__main__":
    main() 