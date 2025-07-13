#!/bin/bash

echo "🚨 开始紧急恢复服务..."

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"
REMOTE_PATH="/home/ubuntu/InterviewPro"

echo "🔍 1. 检查服务器连接..."
if ping -c 1 3.14.247.189 >/dev/null 2>&1; then
    echo "✅ 服务器可达"
else
    echo "❌ 服务器无响应，可能需要重启EC2实例"
    exit 1
fi

echo "🚀 2. 尝试快速重启服务..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml up -d" || {
    echo "❌ 快速重启失败，尝试强制重启..."
    ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml down --remove-orphans && sudo docker-compose -f docker-compose.prod.yml up -d"
}

echo "⏳ 3. 等待服务启动..."
sleep 20

echo "🩺 4. 检查服务状态..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml ps"

echo "🌐 5. 测试网站访问..."
if curl -I --connect-timeout 10 https://offerott.com >/dev/null 2>&1; then
    echo "✅ 网站恢复正常"
else
    echo "❌ 网站仍无法访问，需要进一步排查"
fi

echo "📋 6. 查看错误日志..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml logs --tail=20"

echo "✅ 紧急恢复操作完成" 