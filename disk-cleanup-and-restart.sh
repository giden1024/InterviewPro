#!/bin/bash

echo "🧹 磁盘清理和Docker重启脚本"
echo "=============================="

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📊 1. 检查当前磁盘使用情况..."
ssh -i $KEY_PATH $SERVER "df -h /"

echo -e "\n🧹 2. 清理Docker系统文件..."
ssh -i $KEY_PATH $SERVER "sudo docker system prune -a -f --volumes"

echo -e "\n📝 3. 清理系统日志..."
ssh -i $KEY_PATH $SERVER "sudo journalctl --vacuum-size=50M"

echo -e "\n📦 4. 清理包管理器缓存..."
ssh -i $KEY_PATH $SERVER "sudo apt clean && sudo apt autoclean"

echo -e "\n🗑️ 5. 清理临时文件..."
ssh -i $KEY_PATH $SERVER "sudo rm -rf /tmp/* /var/tmp/* 2>/dev/null || true"

echo -e "\n📊 6. 检查清理后磁盘空间..."
ssh -i $KEY_PATH $SERVER "df -h /"

echo -e "\n🚀 7. 重启Docker服务..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml up -d"

echo -e "\n⏳ 8. 等待服务启动..."
sleep 30

echo -e "\n🔍 9. 检查容器状态..."
ssh -i $KEY_PATH $SERVER "sudo docker ps"

echo -e "\n🌐 10. 测试网站访问..."
sleep 5
curl -I --connect-timeout 10 https://offerott.com/home

echo -e "\n✅ 清理和重启完成！" 