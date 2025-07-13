#!/bin/bash

echo "🔍 查找并修复requirements.txt"
echo "============================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 查找requirements.txt文件位置..."
ssh -i $KEY_PATH $SERVER "find /home/ubuntu/InterviewPro -name 'requirements.txt' -type f"

echo -e "\n📋 2. 查看项目目录结构..."
ssh -i $KEY_PATH $SERVER "ls -la /home/ubuntu/InterviewPro/"

echo -e "\n📋 3. 查看backend目录..."
ssh -i $KEY_PATH $SERVER "ls -la /home/ubuntu/InterviewPro/backend/ 2>/dev/null || echo 'backend目录不存在'"

echo -e "\n📋 4. 如果找到requirements.txt，检查第83行..."
ssh -i $KEY_PATH $SERVER "if [ -f /home/ubuntu/InterviewPro/requirements.txt ]; then sed -n '80,85p' /home/ubuntu/InterviewPro/requirements.txt; else echo 'requirements.txt不在根目录'; fi"

echo -e "\n📋 5. 检查Docker构建上下文..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && find . -name 'requirements.txt' -exec grep -n 'soundfile.*gunicorn' {} \;"

echo -e "\n✅ 查找完成" 