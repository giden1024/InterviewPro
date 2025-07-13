#!/bin/bash

echo "=== InterviewPro快速恢复脚本 ==="
echo "$(date): 开始恢复服务器"

# 等待服务器完全启动
echo "等待服务器响应..."
for i in {1..30}; do
    if ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'whoami' >/dev/null 2>&1; then
        echo "服务器已响应"
        break
    fi
    echo "等待中... ($i/30)"
    sleep 10
done

# 检查磁盘空间
echo -e "\n=== 检查磁盘空间 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'df -h'

# 紧急清理
echo -e "\n=== 紧急清理磁盘空间 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 '
echo "清理Docker资源..."
sudo docker system prune -a -f
echo "清理临时文件..."
sudo rm -rf /tmp/*
echo "清理日志..."
sudo journalctl --vacuum-time=1d
echo "清理npm缓存..."
npm cache clean --force 2>/dev/null || echo "npm cache clean 跳过"
echo "清理完成"
'

# 检查清理效果
echo -e "\n=== 清理后磁盘空间 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'df -h'

# 修复requirements.txt
echo -e "\n=== 修复requirements.txt ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 '
cd /home/ubuntu/InterviewPro
echo "检查beautifulsoup4..."
if ! grep -q "beautifulsoup4" backend/requirements.txt; then
    echo "beautifulsoup4==4.12.2" >> backend/requirements.txt
    echo "已添加beautifulsoup4"
else
    echo "beautifulsoup4已存在"
fi
'

# 重新启动应用
echo -e "\n=== 重新启动应用 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 '
cd /home/ubuntu/InterviewPro
echo "停止现有容器..."
sudo docker-compose -f docker-compose.prod.yml down
echo "启动新容器..."
sudo docker-compose -f docker-compose.prod.yml up -d
echo "等待容器启动..."
sleep 30
'

# 检查服务状态
echo -e "\n=== 检查服务状态 ==="
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'sudo docker ps'

# 测试网站
echo -e "\n=== 测试网站访问 ==="
sleep 10
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://offerott.com/)
echo "网站状态码: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 网站恢复成功！"
else
    echo "❌ 网站仍有问题，状态码: $HTTP_CODE"
fi

echo "$(date): 恢复脚本完成" 