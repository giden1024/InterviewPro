#!/bin/bash

echo "🚨 最终修复方案"
echo "==============="

# 服务器信息
SERVER="ubuntu@3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "🔧 步骤1: 检查并修复requirements.txt..."
ssh -i $KEY_PATH $SERVER << 'EOF'
cd /home/ubuntu/InterviewPro
echo "当前第83行:"
sed -n '83p' requirements.txt | cat -A

echo "修复requirements.txt..."
# 直接重写第83行
sed -i '83s/.*/soundfile==0.12.1/' requirements.txt

echo "修复后第83行:"
sed -n '83p' requirements.txt | cat -A
EOF

echo -e "\n🔧 步骤2: 清理Docker环境..."
ssh -i $KEY_PATH $SERVER "sudo docker system prune -a -f"

echo -e "\n🔧 步骤3: 重新启动服务..."
ssh -i $KEY_PATH $SERVER "cd /home/ubuntu/InterviewPro && sudo docker-compose -f docker-compose.prod.yml down && sudo docker-compose -f docker-compose.prod.yml up --build -d"

echo -e "\n🔧 步骤4: 等待启动..."
sleep 20

echo -e "\n🔧 步骤5: 检查结果..."
ssh -i $KEY_PATH $SERVER "sudo docker ps"

echo -e "\n🔧 步骤6: 测试网站..."
curl -I --connect-timeout 10 https://offerott.com/home

echo -e "\n✅ 修复完成" 