#!/usr/bin/env python3
"""
批量更新历史面试会话为abandoned状态

识别和更新以下情况的会话为abandoned：
1. created状态超过24小时未启动
2. ready状态超过2小时未启动  
3. in_progress状态超过2小时无答案提交
"""

import os
import sys
from datetime import datetime, timedelta

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

def update_historical_sessions():
    """更新历史会话为abandoned状态"""
    try:
        # 导入必要的模块
        from app import create_app
        from app.extensions import db
        from app.models.question import InterviewSession, Answer
        
        # 创建应用上下文
        app = create_app('development')
        
        with app.app_context():
            print("🔍 开始分析历史面试会话...")
            
            # 当前时间
            now = datetime.utcnow()
            
            # 1. 查找created状态超过24小时的会话
            created_cutoff = now - timedelta(hours=24)
            created_sessions = InterviewSession.query.filter(
                InterviewSession.status == 'created',
                InterviewSession.created_at < created_cutoff
            ).all()
            
            print(f"📊 发现 {len(created_sessions)} 个created状态超过24小时的会话")
            
            # 2. 查找ready状态超过2小时的会话
            ready_cutoff = now - timedelta(hours=2)
            ready_sessions = InterviewSession.query.filter(
                InterviewSession.status == 'ready',
                InterviewSession.updated_at < ready_cutoff
            ).all()
            
            print(f"📊 发现 {len(ready_sessions)} 个ready状态超过2小时的会话")
            
            # 3. 查找in_progress状态超过2小时且无最近答案的会话
            inprogress_cutoff = now - timedelta(hours=2)
            
            # 获取所有in_progress状态的会话
            inprogress_sessions = InterviewSession.query.filter(
                InterviewSession.status == 'in_progress',
                InterviewSession.started_at < inprogress_cutoff
            ).all()
            
            # 检查这些会话是否有最近的答案
            abandoned_inprogress = []
            for session in inprogress_sessions:
                # 查找该会话最近的答案
                recent_answer = Answer.query.filter(
                    Answer.session_id == session.id,
                    Answer.answered_at > inprogress_cutoff
                ).first()
                
                if not recent_answer:
                    abandoned_inprogress.append(session)
            
            print(f"📊 发现 {len(abandoned_inprogress)} 个in_progress状态超过2小时且无最近答案的会话")
            
            # 汇总所有需要更新的会话
            all_sessions_to_abandon = created_sessions + ready_sessions + abandoned_inprogress
            
            if not all_sessions_to_abandon:
                print("✅ 没有需要更新为abandoned状态的会话")
                return
            
            print(f"\n📋 总共需要更新 {len(all_sessions_to_abandon)} 个会话为abandoned状态")
            
            # 显示详细信息
            print("\n📄 详细信息:")
            for i, session in enumerate(all_sessions_to_abandon[:10], 1):  # 只显示前10个
                print(f"  {i}. {session.session_id[:8]}... - {session.status} - {session.title[:50]}...")
            
            if len(all_sessions_to_abandon) > 10:
                print(f"  ... 还有 {len(all_sessions_to_abandon) - 10} 个会话")
            
            # 确认是否继续
            response = input(f"\n❓ 确定要将这 {len(all_sessions_to_abandon)} 个会话设置为abandoned状态吗？ (y/N): ")
            
            if response.lower() != 'y':
                print("❌ 操作已取消")
                return
            
            # 执行批量更新
            print("\n🔄 开始批量更新...")
            updated_count = 0
            
            for session in all_sessions_to_abandon:
                try:
                    old_status = session.status
                    session.status = 'abandoned'
                    session.updated_at = now
                    
                    # 如果是in_progress状态但没有started_at，设置它
                    if old_status == 'in_progress' and not session.started_at:
                        session.started_at = session.created_at
                    
                    updated_count += 1
                    
                    if updated_count % 10 == 0:
                        print(f"  ✅ 已更新 {updated_count}/{len(all_sessions_to_abandon)} 个会话")
                
                except Exception as e:
                    print(f"  ❌ 更新会话 {session.session_id} 失败: {e}")
            
            # 提交所有更改
            try:
                db.session.commit()
                print(f"\n🎉 成功更新 {updated_count} 个会话为abandoned状态!")
                
                # 显示更新后的统计
                print("\n📊 更新后的状态分布:")
                status_counts = db.session.query(
                    InterviewSession.status,
                    db.func.count(InterviewSession.id)
                ).group_by(InterviewSession.status).all()
                
                for status, count in status_counts:
                    print(f"  {status}: {count}")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ 提交更改失败: {e}")
                
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    update_historical_sessions() 