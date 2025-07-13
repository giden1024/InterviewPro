#!/bin/bash

echo "📊 监控Docker重建进度"
echo "===================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 检查当前容器状态..."
ssh -i $KEY_PATH $SERVER "sudo docker ps -a"

echo -e "\n📋 2. 检查docker-compose进程..."
ssh -i $KEY_PATH $SERVER "ps aux | grep docker-compose | grep -v grep || echo '无docker-compose进程'"

echo -e "\n📋 3. 查看最新的构建日志..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml logs --tail=20"

echo -e "\n📋 4. 检查端口状态..."
nc -z -v 3.14.247.189 80 443 2>&1 | grep -E "(succeeded|failed)"

echo -e "\n📋 5. 测试网站响应..."
curl -I --connect-timeout 5 https://offerott.com/home 2>/dev/null | head -1 || echo "网站暂时无响应"

echo -e "\n📋 6. 检查磁盘空间..."
ssh -i $KEY_PATH $SERVER "df -h / | tail -1"

echo -e "\n✅ 监控完成" 