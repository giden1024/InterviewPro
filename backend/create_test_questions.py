#!/usr/bin/env python3
"""
创建测试问题和答案数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.question import Question, InterviewSession, Answer, QuestionType, QuestionDifficulty, InterviewType
from app.models.user import User
from app.models.resume import Resume, ResumeStatus
from datetime import datetime, timedelta
import uuid

def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        try:
            # 查找或创建测试用户
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                test_user = User(
                    email='test@example.com',
                    username='testuser',
                    password_hash='hashed_password'  # 在实际应用中应该正确哈希
                )
                db.session.add(test_user)
                db.session.commit()
                print(f"Created test user: {test_user.id}")
            else:
                print(f"Using existing test user: {test_user.id}")
            
            # 查找或创建测试简历
            test_resume = Resume.query.filter_by(user_id=test_user.id).first()
            if not test_resume:
                test_resume = Resume(
                    user_id=test_user.id,
                    filename='test_resume.pdf',
                    original_filename='test_resume.pdf',
                    file_path='/tmp/test_resume.pdf',
                    file_size=1024,
                    file_type='application/pdf',
                    name='测试用户',
                    email='test@example.com',
                    phone='123-456-7890',
                    skills=['Python', 'JavaScript', 'React', 'Flask', 'MySQL'],
                    experience=[
                        {'title': 'Frontend Developer', 'company': 'Tech Corp', 'duration': '2021-2023'},
                        {'title': 'Software Engineer', 'company': 'Startup Inc', 'duration': '2020-2021'}
                    ],
                    education=[
                        {'degree': 'Computer Science', 'university': 'University of Technology', 'year': '2020'}
                    ],
                    status=ResumeStatus.PROCESSED
                )
                db.session.add(test_resume)
                db.session.commit()
                print(f"Created test resume: {test_resume.id}")
            else:
                print(f"Using existing test resume: {test_resume.id}")
            
            # 创建测试面试会话
            sessions_data = [
                {
                    'session_id': str(uuid.uuid4()),
                    'title': 'Mock Interview - Frontend Developer',
                    'interview_type': InterviewType.COMPREHENSIVE,
                    'total_questions': 8
                },
                {
                    'session_id': str(uuid.uuid4()),
                    'title': 'Formal Interview - Software Engineer',
                    'interview_type': InterviewType.TECHNICAL,
                    'total_questions': 15
                }
            ]
            
            created_sessions = []
            for session_data in sessions_data:
                existing_session = InterviewSession.query.filter_by(
                    title=session_data['title'],
                    user_id=test_user.id
                ).first()
                
                if not existing_session:
                    session = InterviewSession(
                        user_id=test_user.id,
                        resume_id=test_resume.id,
                        session_id=session_data['session_id'],
                        title=session_data['title'],
                        interview_type=session_data['interview_type'],
                        total_questions=session_data['total_questions'],
                        status='completed',
                        completed_questions=session_data['total_questions'],
                        total_score=85.5,
                        created_at=datetime.utcnow() - timedelta(days=7),
                        started_at=datetime.utcnow() - timedelta(days=7),
                        completed_at=datetime.utcnow() - timedelta(days=7, hours=1)
                    )
                    db.session.add(session)
                    created_sessions.append(session)
                else:
                    created_sessions.append(existing_session)
            
            db.session.commit()
            print(f"Created/found {len(created_sessions)} test sessions")
            
            # 创建测试问题和答案
            test_questions_data = [
                {
                    'question_text': '请介绍一下你在React开发中的经验，特别是在状态管理方面的实践。',
                    'question_type': QuestionType.TECHNICAL,
                    'difficulty': QuestionDifficulty.MEDIUM,
                    'category': '前端开发',
                    'tags': ['React', '状态管理', 'Redux', 'Context API'],
                    'answer_text': '我在React开发中有3年的经验，主要使用Redux和Context API进行状态管理。在大型项目中，我倾向于使用Redux Toolkit来简化状态管理逻辑，同时结合React Query处理服务器状态。对于组件级别的状态，我会使用useState和useReducer hooks。',
                    'score': 85,
                    'session_index': 0
                },
                {
                    'question_text': '描述一个你在团队协作中遇到的挑战，以及你是如何解决的。',
                    'question_type': QuestionType.BEHAVIORAL,
                    'difficulty': QuestionDifficulty.MEDIUM,
                    'category': '团队协作',
                    'tags': ['团队合作', '沟通', '冲突解决'],
                    'answer_text': '在一个项目中，我们团队对技术选型产生了分歧。我组织了技术评审会议，让每个人展示自己方案的优缺点，最终通过投票和技术考量选择了最适合的方案。这个过程让团队更加团结，也建立了良好的决策机制。',
                    'score': 92,
                    'session_index': 0
                },
                {
                    'question_text': '如何优化React应用的性能？请举出具体的优化策略。',
                    'question_type': QuestionType.TECHNICAL,
                    'difficulty': QuestionDifficulty.HARD,
                    'category': '性能优化',
                    'tags': ['React', '性能优化', 'memo', 'useMemo', 'useCallback'],
                    'answer_text': '我通常从以下几个方面优化React应用性能：1) 使用React.memo包装组件避免不必要的重渲染；2) 使用useMemo和useCallback缓存计算结果和函数；3) 代码分割和懒加载；4) 虚拟化长列表；5) 优化bundle大小；6) 使用React DevTools Profiler分析性能瓶颈。',
                    'score': 88,
                    'session_index': 1
                },
                {
                    'question_text': '请说说你对这个职位的理解，以及为什么你认为自己适合这个角色。',
                    'question_type': QuestionType.BEHAVIORAL,
                    'difficulty': QuestionDifficulty.EASY,
                    'category': '职业规划',
                    'tags': ['职业发展', '自我认知', '匹配度'],
                    'answer_text': '我对这个前端开发职位非常感兴趣，因为它与我的技能和职业目标高度匹配。我有扎实的JavaScript基础和丰富的React开发经验，同时具备良好的设计感和用户体验意识。我相信我能为团队带来技术价值和创新思维。',
                    'score': 90,
                    'session_index': 0
                },
                {
                    'question_text': '在微服务架构中，前端如何处理跨服务的数据聚合和状态同步？',
                    'question_type': QuestionType.TECHNICAL,
                    'difficulty': QuestionDifficulty.HARD,
                    'category': '架构设计',
                    'tags': ['微服务', '前端架构', '数据聚合', 'BFF'],
                    'answer_text': '在微服务架构中，我会使用BFF（Backend for Frontend）模式来处理数据聚合。前端通过GraphQL或RESTful API与BFF通信，BFF负责调用多个微服务并聚合数据。对于状态同步，可以使用WebSocket或Server-Sent Events实现实时更新，配合Redux或Zustand进行状态管理。',
                    'score': 87,
                    'session_index': 1
                }
            ]
            
            # 创建问题和答案
            for i, q_data in enumerate(test_questions_data):
                session = created_sessions[q_data['session_index']]
                
                # 检查问题是否已存在
                existing_question = Question.query.filter_by(
                    question_text=q_data['question_text'],
                    user_id=test_user.id
                ).first()
                
                if not existing_question:
                    # 创建问题
                    question = Question(
                        resume_id=test_resume.id,
                        user_id=test_user.id,
                        session_id=session.id,
                        question_text=q_data['question_text'],
                        question_type=q_data['question_type'],
                        difficulty=q_data['difficulty'],
                        category=q_data['category'],
                        tags=q_data['tags'],
                        created_at=datetime.utcnow() - timedelta(days=7-i, hours=i)
                    )
                    db.session.add(question)
                    db.session.flush()  # 获取question.id
                    
                    # 创建答案
                    answer = Answer(
                        session_id=session.id,
                        question_id=question.id,
                        user_id=test_user.id,
                        answer_text=q_data['answer_text'],
                        score=q_data['score'],
                        response_time=120 + i * 30,  # 模拟回答时间
                        answered_at=datetime.utcnow() - timedelta(days=7-i, hours=i, minutes=30)
                    )
                    db.session.add(answer)
                    print(f"Created question {i+1}: {q_data['question_text'][:50]}...")
                else:
                    print(f"Question already exists: {q_data['question_text'][:50]}...")
            
            db.session.commit()
            print("✅ Test data created successfully!")
            print(f"📊 User ID: {test_user.id}")
            print(f"📄 Resume ID: {test_resume.id}")
            print(f"🎯 Sessions: {len(created_sessions)}")
            print(f"❓ Questions: {len(test_questions_data)}")
            
            return test_user.id
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test data: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == '__main__':
    user_id = create_test_data()
    if user_id:
        print(f"\n🔑 Test user ID: {user_id}")
        print("You can use this user ID for testing the API.") 