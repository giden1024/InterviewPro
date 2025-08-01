#!/bin/bash
# 在AWS服务器上执行此脚本

echo "🔄 更新InterviewPro服务器代码"
echo "==========================="

# 切换到项目目录
cd /home/ec2-user/InterviewPro

echo "🛑 停止现有服务"
docker-compose -f docker-compose.prod.yml down

echo "🗑️  清理Docker缓存"
docker system prune -f
docker image prune -f

echo "🔄 拉取最新代码"
git pull origin main

echo "🏗️  重建并启动服务"
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate

echo "⏳ 等待服务启动"
sleep 30

echo "📊 检查服务状态"
docker-compose -f docker-compose.prod.yml ps

echo "🧪 测试API健康状态"
curl -s https://offerott.com/health | jq .

echo "✅ 部署完成"
