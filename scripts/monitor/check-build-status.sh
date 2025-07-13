#!/bin/bash

echo "🔍 检查Docker构建状态"
echo "===================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 查看Docker镜像..."
ssh -i $KEY_PATH $SERVER "sudo docker images"

echo -e "\n📋 2. 尝试手动启动服务..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml up -d"

echo -e "\n📋 3. 检查启动后的容器..."
ssh -i $KEY_PATH $SERVER "sudo docker ps"

echo -e "\n📋 4. 如果启动失败，查看完整日志..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml logs"

echo -e "\n📋 5. 检查系统日志..."
ssh -i $KEY_PATH $SERVER "sudo journalctl -u docker.service --no-pager -n 10"

echo -e "\n✅ 检查完成" 