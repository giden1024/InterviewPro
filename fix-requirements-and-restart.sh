#!/bin/bash

echo "🔧 修复requirements.txt并重启Docker服务"
echo "======================================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 查看当前requirements.txt第83行..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro/backend && sed -n '80,85p' requirements.txt"

echo -e "\n📋 2. 修复requirements.txt格式错误..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro/backend && sed -i 's/soundfile==0.12.1 gunicorn==21.2.0/soundfile==0.12.1/' requirements.txt && echo 'gunicorn==21.2.0' >> requirements.txt"

echo -e "\n📋 3. 验证修复结果..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro/backend && sed -n '80,90p' requirements.txt"

echo -e "\n📋 4. 清除损坏的Docker构建缓存..."
ssh -i $KEY_PATH $SERVER "sudo docker builder prune -a -f"

echo -e "\n📋 5. 重新启动Docker服务..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml up --build -d"

echo -e "\n📋 6. 检查启动结果..."
sleep 10
ssh -i $KEY_PATH $SERVER "sudo docker ps"

echo -e "\n📋 7. 测试网站..."
curl -I --connect-timeout 10 https://offerott.com/home

echo -e "\n✅ 修复完成" 