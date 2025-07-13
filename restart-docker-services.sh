#!/bin/bash

echo "🚀 重启InterviewPro Docker服务..."
echo "================================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"
REMOTE_PATH="/home/ubuntu/InterviewPro"

echo "📋 1. 检查当前Docker容器状态..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml ps"

echo -e "\n🔄 2. 重启Docker服务..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml down"

echo -e "\n🆙 3. 启动Docker服务..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml up -d"

echo -e "\n⏳ 4. 等待服务启动..."
sleep 10

echo -e "\n🔍 5. 检查服务状态..."
ssh -i $KEY_PATH $SERVER "cd $REMOTE_PATH && sudo docker-compose -f docker-compose.prod.yml ps"

echo -e "\n🌐 6. 测试网站访问..."
sleep 5
curl -I --connect-timeout 10 https://offerott.com/home

echo -e "\n✅ 恢复完成！" 