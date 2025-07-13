#!/usr/bin/env python3
"""
生产环境数据库初始化脚本
"""

import os
import sys
import logging
from datetime import datetime

# 添加应用路径
sys.path.insert(0, '/app')

try:
    from app import create_app
    from app.extensions import db
    from app.models import User, Resume, Question, InterviewSession, Answer
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在正确的环境中运行此脚本")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_production_database():
    """初始化生产数据库"""
    logger.info("🚀 开始初始化生产数据库...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 检查数据库连接
            db.session.execute('SELECT 1')
            logger.info("✅ 数据库连接成功")
            
            # 创建所有表
            db.create_all()
            logger.info("✅ 数据库表创建成功")
            
            # 检查是否已有管理员用户
            admin_email = 'admin@interviewpro.com'
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if existing_admin:
                logger.info(f"ℹ️ 管理员用户 {admin_email} 已存在")
            else:
                # 创建管理员用户
                admin_password = os.getenv('ADMIN_PASSWORD', 'AdminPassword123!')
                admin_user = User(
                    email=admin_email,
                    name='系统管理员'
                )
                admin_user.set_password(admin_password)
                
                db.session.add(admin_user)
                db.session.commit()
                
                logger.info(f"✅ 管理员用户创建成功")
                logger.info(f"   邮箱: {admin_email}")
                logger.info(f"   密码: {admin_password}")
                logger.warning("⚠️ 请尽快修改默认管理员密码！")
            
            # 创建测试用户（可选）
            if os.getenv('CREATE_TEST_USER', 'false').lower() == 'true':
                test_email = 'test@interviewpro.com'
                existing_test = User.query.filter_by(email=test_email).first()
                
                if not existing_test:
                    test_user = User(
                        email=test_email,
                        name='测试用户'
                    )
                    test_user.set_password('TestPassword123!')
                    
                    db.session.add(test_user)
                    db.session.commit()
                    
                    logger.info(f"✅ 测试用户创建成功: {test_email}")
            
            # 显示数据库统计信息
            user_count = User.query.count()
            resume_count = Resume.query.count()
            question_count = Question.query.count()
            session_count = InterviewSession.query.count()
            answer_count = Answer.query.count()
            
            logger.info("📊 数据库统计:")
            logger.info(f"   用户数量: {user_count}")
            logger.info(f"   简历数量: {resume_count}")
            logger.info(f"   问题数量: {question_count}")
            logger.info(f"   面试会话: {session_count}")
            logger.info(f"   答案数量: {answer_count}")
            
            logger.info("🎉 数据库初始化完成！")
            
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            db.session.rollback()
            raise
        finally:
            db.session.close()

def check_database_health():
    """检查数据库健康状态"""
    logger.info("🔍 检查数据库健康状态...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 基本连接测试
            result = db.session.execute('SELECT version()')
            version = result.scalar()
            logger.info(f"✅ 数据库版本: {version}")
            
            # 检查表是否存在
            tables = ['users', 'resumes', 'questions', 'interview_sessions', 'answers']
            for table in tables:
                result = db.session.execute(f"SELECT COUNT(*) FROM {table}")
                count = result.scalar()
                logger.info(f"✅ 表 {table}: {count} 条记录")
            
            logger.info("✅ 数据库健康检查通过")
            
        except Exception as e:
            logger.error(f"❌ 数据库健康检查失败: {e}")
            raise
        finally:
            db.session.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='生产数据库管理工具')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--check', action='store_true', help='检查数据库健康状态')
    parser.add_argument('--create-admin', action='store_true', help='创建管理员用户')
    
    args = parser.parse_args()
    
    if args.check:
        check_database_health()
    elif args.init:
        init_production_database()
    elif args.create_admin:
        # 仅创建管理员用户的逻辑
        app = create_app()
        with app.app_context():
            admin_email = input("请输入管理员邮箱: ")
            admin_password = input("请输入管理员密码: ")
            admin_name = input("请输入管理员姓名: ")
            
            existing_admin = User.query.filter_by(email=admin_email).first()
            if existing_admin:
                logger.warning(f"用户 {admin_email} 已存在")
            else:
                admin_user = User(email=admin_email, name=admin_name)
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                db.session.commit()
                logger.info(f"✅ 管理员用户 {admin_email} 创建成功")
    else:
        # 默认执行初始化
        init_production_database() 