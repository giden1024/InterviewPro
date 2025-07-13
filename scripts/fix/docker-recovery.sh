#!/bin/bash

echo "🔄 正在恢复Docker服务..."

# 重启Docker服务
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml down && sudo docker-compose -f docker-compose.prod.yml up -d'

echo "等待服务启动..."
sleep 30

echo "检查服务状态..."
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'sudo docker ps'

echo "测试网站访问..."
curl -I --connect-timeout 10 https://offerott.com/home

echo "恢复完成！" 