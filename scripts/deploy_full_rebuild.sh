#!/bin/bash
# 完整重构建部署脚本 - 仅在依赖或数据库修改时使用
set -e

echo "🏗️  开始完整重构建部署..."
echo "⚠️  这将需要较长时间，请耐心等待..."

# 提交代码
echo "💾 提交代码..."
git add .
git commit -m "Full rebuild deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push origin main

# 服务器完整部署
echo "🌐 服务器完整重构建..."
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    echo "📥 拉取最新代码..."
    git pull
    
    echo "🛑 停止所有服务..."
    docker-compose -f docker-compose.prod.yml down
    
    echo "🧹 清理Docker缓存..."
    docker system prune -f
    
    echo "🏗️  重新构建镜像 (无缓存)..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    echo "🚀 启动所有服务..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "⏳ 等待服务启动..."
    sleep 30
    
    echo "🔍 检查服务状态..."
    docker-compose -f docker-compose.prod.yml ps
    
    echo "✅ 完整重构建完成"
EOF

echo "🎉 完整重构建部署完成！"

# 验证部署
echo "🔍 验证部署..."
sleep 10
curl -s https://offerott.com/api/v1/health || echo "Backend health check failed"
curl -s https://offerott.com/ > /dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend check failed" 