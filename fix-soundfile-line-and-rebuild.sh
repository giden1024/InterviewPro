#!/bin/bash

echo "🔧 修复soundfile行末尾空格并重建Docker"
echo "==================================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 修复第83行末尾的空格..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sed -i 's/soundfile==0.12.1 $/soundfile==0.12.1/' requirements.txt"

echo -e "\n📋 2. 验证修复结果..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && tail -5 requirements.txt"

echo -e "\n📋 3. 清除所有Docker构建缓存..."
ssh -i $KEY_PATH $SERVER "sudo docker system prune -a -f"

echo -e "\n📋 4. 停止现有容器..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml down"

echo -e "\n📋 5. 重新构建并启动服务..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml up --build -d"

echo -e "\n📋 6. 等待构建完成并检查容器状态..."
sleep 30
ssh -i $KEY_PATH $SERVER "sudo docker ps"

echo -e "\n📋 7. 检查容器日志..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml logs --tail=10"

echo -e "\n📋 8. 测试网站..."
curl -I --connect-timeout 10 https://offerott.com/home

echo -e "\n✅ 修复完成" 