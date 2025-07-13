#!/bin/bash

echo "🔧 直接修复服务器上的requirements.txt"
echo "================================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 查看当前第83行内容..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sed -n '83p' requirements.txt | cat -A"

echo -e "\n📋 2. 重新创建干净的requirements.txt末尾..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && head -n 82 requirements.txt > requirements_clean.txt && echo 'soundfile==0.12.1' >> requirements_clean.txt && mv requirements_clean.txt requirements.txt"

echo -e "\n📋 3. 验证修复结果..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && tail -5 requirements.txt"

echo -e "\n📋 4. 验证无隐藏字符..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sed -n '83p' requirements.txt | cat -A"

echo -e "\n📋 5. 清除所有Docker缓存..."
ssh -i $KEY_PATH $SERVER "sudo docker system prune -a -f && sudo docker builder prune -a -f"

echo -e "\n📋 6. 重新构建服务..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml up --build -d"

echo -e "\n✅ 修复完成" 