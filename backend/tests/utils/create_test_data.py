#!/usr/bin/env python3
"""
Create test data for AI question generation testing
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

def create_test_data():
    """Create test user and resume data"""
    try:
        from app import create_app
        from app.models.user import User
        from app.models.resume import Resume, ResumeStatus
        from app.extensions import db
        
        app = create_app('development')
        with app.app_context():
            # 查找测试用户
            user = User.query.filter_by(email="test_ai_questions@example.com").first()
            if not user:
                print("❌ Test user not found. Please run the test script first to create the user.")
                return False
            
            print(f"✅ Found test user: {user.email}, ID: {user.id}")
            
            # 检查是否已有测试简历
            existing_resume = Resume.query.filter_by(
                user_id=user.id, 
                original_filename="test_resume.pdf"
            ).first()
            
            if existing_resume:
                print(f"✅ Test resume already exists, ID: {existing_resume.id}")
                return True
            
            # 创建测试简历
            test_resume = Resume(
                user_id=user.id,
                filename=f"test_resume_{user.id}.pdf",
                original_filename="test_resume.pdf",
                file_path="/tmp/test_resume.pdf",
                file_size=1024000,
                file_type="pdf",
                status=ResumeStatus.PROCESSED,
                name="John Smith",
                email="john.smith@example.com",
                phone="+1-555-0123",
                skills=["Python", "JavaScript", "React", "Flask", "Docker", "AWS", "Machine Learning"],
                experience=[
                    {
                        "title": "Senior Software Engineer",
                        "company": "Tech Corporation",
                        "duration": "2020-2023",
                        "description": "Led development of AI-powered web applications"
                    },
                    {
                        "title": "Full Stack Developer", 
                        "company": "StartupXYZ",
                        "duration": "2018-2020",
                        "description": "Built scalable web applications using React and Node.js"
                    }
                ],
                education=[
                    {
                        "degree": "Master of Computer Science",
                        "university": "Stanford University",
                        "year": "2018"
                    }
                ],
                raw_text="""
                John Smith
                Senior Software Engineer
                Email: john.smith@example.com
                Phone: +1-555-0123
                
                Professional Summary:
                Experienced software engineer with 5+ years of expertise in full-stack development,
                AI/ML integration, and cloud technologies. Proven track record of leading technical
                teams and delivering scalable solutions.
                
                Technical Skills:
                - Programming: Python, JavaScript, TypeScript, Java
                - Frameworks: React, Flask, Django, Express.js
                - Cloud: AWS, Docker, Kubernetes
                - AI/ML: TensorFlow, PyTorch, scikit-learn
                - Databases: PostgreSQL, MongoDB, Redis
                """
            )
            
            db.session.add(test_resume)
            db.session.commit()
            
            print(f"✅ Test resume created successfully, ID: {test_resume.id}")
            print(f"   📄 Name: {test_resume.name}")
            print(f"   📄 Skills: {len(test_resume.skills)} skills")
            print(f"   📄 Experience: {len(test_resume.experience)} positions")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Creating test data for AI question generation...")
    success = create_test_data()
    if success:
        print("🎉 Test data created successfully!")
    else:
        print("❌ Failed to create test data.")
        sys.exit(1) 