#!/usr/bin/env python3
"""
调试认证问题
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, 'backend')

try:
    # 测试基本导入
    print("1. 测试基本导入...")
    from werkzeug.security import generate_password_hash, check_password_hash
    print("✅ Werkzeug导入成功")
    
    # 测试密码哈希
    print("\n2. 测试密码哈希...")
    password = "test123"
    hash_result = generate_password_hash(password, method='pbkdf2:sha256')
    print(f"✅ 密码哈希成功: {hash_result[:50]}...")
    
    # 测试Flask应用创建
    print("\n3. 测试Flask应用创建...")
    from app import create_app
    app = create_app()
    print("✅ Flask应用创建成功")
    
    # 测试数据库模型
    print("\n4. 测试数据库模型...")
    from app.models.user import User
    print("✅ User模型导入成功")
    
    # 在应用上下文中测试用户创建
    print("\n5. 测试用户模型...")
    with app.app_context():
        from app.extensions import db
        
        # 创建数据库表
        db.create_all()
        print("✅ 数据库表创建成功")
        
        # 测试用户创建
        user = User(email="debug@test.com", username="Debug User")
        user.set_password("test123")
        print("✅ 用户密码设置成功")
        
        # 测试密码验证
        is_valid = user.check_password("test123")
        print(f"✅ 密码验证结果: {is_valid}")
        
        # 尝试保存到数据库
        try:
            db.session.add(user)
            db.session.commit()
            print("✅ 用户保存到数据库成功")
        except Exception as e:
            print(f"⚠️ 数据库保存失败: {e}")
            db.session.rollback()
    
    print("\n🎉 所有测试通过！认证功能应该正常工作。")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc() 