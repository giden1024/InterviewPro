#!/usr/bin/env python3
"""
Database Initialization Script for InterviewGenius AI
Creates all necessary tables for the question generation system
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def init_database():
    """Initialize the database with all required tables"""
    try:
        from app import create_app
        from app.extensions import db
        from app.models.user import User
        from app.models.resume import Resume, ResumeStatus
        from app.models.question import Question, InterviewSession, Answer, QuestionType, QuestionDifficulty, InterviewType
        
        print("🚀 Initializing InterviewGenius AI Database...")
        
        # Create Flask app
        app = create_app('development')
        
        with app.app_context():
            # Drop all tables (for development)
            print("🗑️  Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("📋 Creating database tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"✅ Successfully created {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   📄 {table}")
            
            # Create a test user for development
            test_user = User(
                email="developer@interviewgenius.ai",
                username="Developer"
            )
            test_user.set_password("dev123")
            
            db.session.add(test_user)
            db.session.commit()
            
            print(f"👤 Created test user: {test_user.email}")
            print("🎉 Database initialization completed successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def verify_models():
    """Verify that all models can be imported and have proper relationships"""
    try:
        from app.models.user import User
        from app.models.resume import Resume
        from app.models.question import Question, InterviewSession, Answer
        
        print("🔍 Verifying model definitions...")
        
        # Check model attributes
        models_info = {
            'User': {
                'model': User,
                'key_fields': ['id', 'email', 'password_hash', 'created_at']
            },
            'Resume': {
                'model': Resume,
                'key_fields': ['id', 'user_id', 'filename', 'status', 'skills', 'experience']
            },
            'InterviewSession': {
                'model': InterviewSession,
                'key_fields': ['id', 'user_id', 'resume_id', 'session_id', 'status']
            },
            'Question': {
                'model': Question,
                'key_fields': ['id', 'user_id', 'resume_id', 'session_id', 'question_text', 'question_type']
            },
            'Answer': {
                'model': Answer,
                'key_fields': ['id', 'user_id', 'question_id', 'session_id', 'answer_text']
            }
        }
        
        for model_name, info in models_info.items():
            model_class = info['model']
            missing_fields = []
            
            for field in info['key_fields']:
                if not hasattr(model_class, field):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️  {model_name} missing fields: {missing_fields}")
            else:
                print(f"✅ {model_name} model verified")
        
        print("✅ Model verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Model verification failed: {e}")
        return False

def main():
    """Main initialization function"""
    print("🤖 InterviewGenius AI - Database Initialization")
    print("=" * 50)
    
    # Verify models first
    if not verify_models():
        print("❌ Model verification failed. Please fix model definitions.")
        sys.exit(1)
    
    # Initialize database
    if not init_database():
        print("❌ Database initialization failed.")
        sys.exit(1)
    
    print("\n🎯 Next Steps:")
    print("1. Start the Flask application: python run.py")
    print("2. Run the test suite: python ../test_ai_question_system.py")
    print("3. Access the API at: http://localhost:5000")
    
    print("\n🔗 Available API Endpoints:")
    endpoints = [
        "POST /api/v1/auth/register - User registration",
        "POST /api/v1/auth/login - User login",
        "GET  /api/v1/questions - Get user questions",
        "POST /api/v1/questions/generate - Generate questions",
        "GET  /api/v1/questions/sessions - Get interview sessions",
        "GET  /api/v1/questions/stats - Get question statistics"
    ]
    
    for endpoint in endpoints:
        print(f"   📡 {endpoint}")

if __name__ == "__main__":
    main() 