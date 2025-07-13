#!/bin/bash

echo "🔍 Docker启动状态检查"
echo "===================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 检查运行中的容器..."
ssh -i $KEY_PATH $SERVER "sudo docker ps"

echo -e "\n📋 2. 检查所有容器（包括停止的）..."
ssh -i $KEY_PATH $SERVER "sudo docker ps -a"

echo -e "\n📋 3. 检查Docker Compose状态..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml ps"

echo -e "\n📋 4. 查看最近的容器日志..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml logs --tail=10"

echo -e "\n🌐 5. 测试网站响应..."
curl -I --connect-timeout 10 https://offerott.com/home

echo -e "\n🔌 6. 检查端口状态..."
echo "端口80:" && nc -z -w3 3.14.247.189 80 && echo "✅ 开放" || echo "❌ 关闭"
echo "端口443:" && nc -z -w3 3.14.247.189 443 && echo "✅ 开放" || echo "❌ 关闭"

echo -e "\n📊 7. 检查磁盘空间..."
ssh -i $KEY_PATH $SERVER "df -h / | tail -1"

echo -e "\n✅ 检查完成" 