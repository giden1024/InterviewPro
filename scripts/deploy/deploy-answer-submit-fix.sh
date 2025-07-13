#!/bin/bash

echo "🔧 开始完全重新部署修复答案提交问题..."

# 生产服务器信息
SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"
REMOTE_PATH="/home/ubuntu/InterviewPro"

echo "📦 1. 上传修复后的代码文件..."
scp -i $KEY_PATH backend/app/api/interviews.py $SERVER:$REMOTE_PATH/app/api/
scp -i $KEY_PATH backend/app/services/interview_service.py $SERVER:$REMOTE_PATH/app/services/

echo "🛑 2. 停止现有服务..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml down"

echo "🗑️ 3. 清理Docker镜像缓存..."
ssh -i $KEY_PATH $SERVER "sudo docker system prune -f && sudo docker image prune -a -f"

echo "🔨 4. 重新构建并启动服务..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml build --no-cache backend"
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml up -d"

echo "⏳ 5. 等待服务启动..."
sleep 15

echo "🩺 6. 检查服务状态..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml ps"

echo "📋 7. 查看最新日志..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml logs backend --tail=10"

echo "✅ 完全重新部署完成！"
echo "🧪 请重新测试答案提交功能：https://offerott.com/api/v1/interviews/{session_id}/answer" 