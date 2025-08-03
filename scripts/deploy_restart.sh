#!/bin/bash
# 服务重启部署脚本 - 适用于配置修改
set -e

echo "🔄 开始服务重启部署..."

# 同步代码
echo "📋 同步代码..."
git add .
git commit -m "Restart deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push origin main

# 服务器部署
echo "🌐 服务器重启部署..."
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    # 拉取最新代码
    git pull
    
    # 检查哪些服务需要重启
    echo "🔍 检查服务状态..."
    docker-compose -f docker-compose.prod.yml ps
    
    # 重启后端服务 (保持数据库和Redis运行)
    echo "🔄 重启后端服务..."
    docker-compose -f docker-compose.prod.yml restart backend
    
    # 重新构建并重启前端 (如果有前端修改)
    if git diff HEAD~1 --name-only | grep -q "frontend/"; then
        echo "🔄 重新构建前端..."
        cd frontend
        npm run build
        cd ..
        docker-compose -f docker-compose.prod.yml restart nginx
    fi
    
    # 等待服务启动
    sleep 10
    
    echo "✅ 服务重启完成"
EOF

echo "🎉 重启部署完成！"

# 验证部署
echo "🔍 验证服务状态..."
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 'docker-compose -f /home/ec2-user/InterviewPro/docker-compose.prod.yml ps' 