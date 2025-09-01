#!/usr/bin/env python3

import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

def test_create_question_direct():
    """直接测试创建问题功能"""
    try:
        from backend.app import create_app
        from backend.app.models.question import Question, InterviewSession, InterviewType, QuestionType, QuestionDifficulty, Answer
        from backend.app.models.resume import Resume
        from backend.app.models.user import User
        from backend.app.extensions import db
        from datetime import datetime
        import uuid
        
        app = create_app()
        with app.app_context():
            print("🔍 开始调试创建问题功能...")
            
            # 获取用户
            user_id = 3  # 从之前的测试中获取
            user = User.query.get(user_id)
            if not user:
                print(f"❌ 用户 {user_id} 不存在")
                return
            print(f"✅ 找到用户: {user.username}")
            
            # 获取用户的最新简历
            latest_resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.uploaded_at.desc()).first()
            if not latest_resume:
                print("❌ 用户没有简历")
                return
            print(f"✅ 找到简历: {latest_resume.id}")
            
            # 创建或获取面试会话
            session_title = f"Manual Questions - {datetime.now().strftime('%Y-%m-%d')}"
            session = InterviewSession.query.filter_by(
                user_id=user_id,
                resume_id=latest_resume.id,
                title=session_title,
                interview_type=InterviewType.COMPREHENSIVE
            ).first()
            
            if not session:
                session_id = str(uuid.uuid4())
                session = InterviewSession(
                    user_id=user_id,
                    resume_id=latest_resume.id,
                    session_id=session_id,
                    title=session_title,
                    interview_type=InterviewType.COMPREHENSIVE,
                    total_questions=0,
                    status='ready'
                )
                db.session.add(session)
                db.session.flush()  # 获取session.id
                print(f"✅ 创建新会话: {session.id}")
            else:
                print(f"✅ 使用现有会话: {session.id}")
            
            # 创建问题
            print("📝 创建问题...")
            question = Question(
                user_id=user_id,
                resume_id=latest_resume.id,
                session_id=session.id,
                question_text="请介绍一下React的生命周期方法",
                question_type=QuestionType.TECHNICAL,
                difficulty=QuestionDifficulty.MEDIUM,
                category="前端开发",
                tags=["React", "生命周期", "前端"],
                expected_answer="React的生命周期方法包括componentDidMount等",
                evaluation_criteria={},
                ai_context={}
            )
            
            db.session.add(question)
            db.session.flush()  # 获取question.id
            print(f"✅ 问题创建成功: {question.id}")
            
            # 创建答案记录
            print("📋 创建答案记录...")
            answer = Answer(
                user_id=user_id,
                question_id=question.id,
                session_id=session.id,
                answer_text="React的生命周期方法包括componentDidMount等",
                response_time=0,
                score=None,
                ai_feedback=None,
                answered_at=datetime.utcnow()
            )
            
            db.session.add(answer)
            print(f"✅ 答案记录创建成功")
            
            # 更新会话问题数量
            session.total_questions += 1
            
            # 提交所有更改
            db.session.commit()
            print("✅ 所有数据已保存到数据库")
            
            print(f"📊 最终结果:")
            print(f"   - 问题ID: {question.id}")
            print(f"   - 答案ID: {answer.id}")
            print(f"   - 会话ID: {session.id}")
            print(f"   - 会话问题总数: {session.total_questions}")
            
    except Exception as e:
        print(f"❌ 出现错误: {e}")
        print("📋 详细错误信息:")
        traceback.print_exc()

if __name__ == "__main__":
    test_create_question_direct() 