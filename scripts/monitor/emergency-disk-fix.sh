#!/bin/bash

echo "=== 紧急磁盘空间修复脚本 ==="
echo "$(date): 开始诊断服务器问题"

# 检查磁盘空间
echo -e "\n=== 检查磁盘空间 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'df -h'

# 检查Docker状态
echo -e "\n=== 检查Docker状态 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'sudo docker ps -a'

# 清理磁盘空间
echo -e "\n=== 清理磁盘空间 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 '
cd /home/ubuntu/InterviewPro
echo "清理Docker资源..."
sudo docker system prune -a -f
echo "清理npm缓存..."
npm cache clean --force 2>/dev/null || echo "npm cache clean 跳过"
echo "清理临时文件..."
sudo rm -rf /tmp/*
echo "清理日志文件..."
sudo journalctl --vacuum-time=1d
'

# 检查清理后的磁盘空间
echo -e "\n=== 清理后磁盘空间 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'df -h'

# 重新启动容器
echo -e "\n=== 重新启动Docker容器 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 '
cd /home/ubuntu/InterviewPro
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d
'

# 检查最终状态
echo -e "\n=== 检查最终状态 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'sudo docker ps'

echo -e "\n=== 测试网站访问 ==="
sleep 5
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" https://offerott.com/

echo "$(date): 修复脚本完成" 