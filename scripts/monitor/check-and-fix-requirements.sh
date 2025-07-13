#!/bin/bash

echo "🔧 检查并修复requirements.txt格式"
echo "================================"

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 查看完整的requirements.txt..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && cat -n requirements.txt"

echo -e "\n📋 2. 查找可能的格式错误..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && grep -n 'gunicorn' requirements.txt || echo '未找到gunicorn'"

echo -e "\n📋 3. 检查是否有重复或合并的包名..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && grep -n -E '[a-zA-Z]==.*[a-zA-Z]==.*' requirements.txt || echo '未找到合并包名'"

echo -e "\n📋 4. 检查Dockerfile.prod中的处理..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && cat Dockerfile.prod"

echo -e "\n✅ 检查完成" 