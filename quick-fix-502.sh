#!/bin/bash

# 快速修复502错误脚本

echo "🔧 快速修复 InterviewPro 502错误"
echo "================================="

SERVER_IP="3.14.247.189"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"
SSH_USER="ubuntu"

echo "🔍 连接服务器并诊断问题..."

# 一步到位的修复命令
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "
echo '=== 服务器状态诊断 ==='
echo '--- Docker容器状态 ---'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo
echo '--- Nginx系统服务状态 ---'
sudo systemctl status nginx --no-pager | head -10
echo
echo '=== 开始修复 ==='
echo '1. 重启系统Nginx...'
sudo systemctl restart nginx
sudo systemctl enable nginx
echo '2. 重启Docker服务...'
cd /home/ubuntu/InterviewPro
docker-compose down
sleep 5
docker-compose up -d
echo '3. 等待服务启动...'
sleep 15
echo '4. 检查最终状态...'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
sudo systemctl is-active nginx && echo '✅ Nginx运行正常' || echo '❌ Nginx未运行'
curl -s http://localhost/ > /dev/null && echo '✅ 本地前端正常' || echo '❌ 本地前端异常'
echo '=== 修复完成 ==='
"

echo ""
echo "🌐 测试外部访问..."
sleep 5

# 测试网站访问
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "https://offerott.com/" || echo "000")
echo "外部访问状态码: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ 修复成功！网站现在可以正常访问"
    echo "🌐 网站地址: https://offerott.com/"
elif [ "$HTTP_STATUS" = "502" ]; then
    echo "❌ 502错误仍然存在"
    echo "建议运行完整的诊断脚本: ./fix-502-error.sh"
else
    echo "⚠️ 网站状态码: $HTTP_STATUS"
    echo "可能需要进一步检查"
fi

echo ""
echo "🔧 修复完成！" 