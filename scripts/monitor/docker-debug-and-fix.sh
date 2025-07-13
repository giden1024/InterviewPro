#!/bin/bash

echo "🔧 Docker调试和修复脚本"
echo "======================"

SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📋 1. 检查Docker服务状态..."
ssh -i $KEY_PATH $SERVER "sudo systemctl status docker --no-pager -l"

echo -e "\n📋 2. 检查docker-compose配置..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && cat docker-compose.prod.yml"

echo -e "\n📋 3. 尝试启动服务（显示详细输出）..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml up --build -d"

echo -e "\n📋 4. 检查启动后的容器状态..."
ssh -i $KEY_PATH $SERVER "sudo docker ps"

echo -e "\n📋 5. 如果失败，查看详细日志..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml logs"

echo -e "\n✅ 调试完成" 