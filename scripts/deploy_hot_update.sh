#!/bin/bash
# 热更新部署脚本 - 适用于纯代码修改
set -e

echo "🔥 开始热更新部署..."

# 检查本地修改
echo "📋 检查本地修改..."
git status --porcelain

# 提交代码
echo "💾 提交代码..."
git add .
git commit -m "Hot update: $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push origin main

# 服务器热更新
echo "🌐 服务器热更新..."
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    # 拉取最新代码
    git pull
    
    # 热更新后端代码 (不重启容器)
    docker cp backend/app/. interviewpro-backend:/app/app/
    docker cp backend/run_complete.py interviewpro-backend:/app/
    
    # 重启后端进程 (Gunicorn 会自动重载)
    docker exec interviewpro-backend pkill -HUP gunicorn || true
    
    # 热更新前端代码
    cd frontend
    npm run build
    docker cp dist/. interviewpro-nginx:/usr/share/nginx/html/
    
    echo "✅ 热更新完成"
EOF

echo "🎉 热更新部署完成！"

# 验证部署
echo "🔍 验证部署..."
sleep 5
curl -s https://offerott.com/api/v1/health || echo "Backend health check failed"
curl -s https://offerott.com/ > /dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend check failed" 