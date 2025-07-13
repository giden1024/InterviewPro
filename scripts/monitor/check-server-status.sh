#!/bin/bash

echo "🔍 检查服务器状态 - $(date)"
echo "================================="

SERVER_IP="3.14.247.189"

# 快速端口检查
echo "📡 检查关键端口..."
echo "SSH (22):" && nc -z -w3 $SERVER_IP 22 && echo "✅ 开放" || echo "❌ 关闭"
echo "HTTP (80):" && nc -z -w3 $SERVER_IP 80 && echo "✅ 开放" || echo "❌ 关闭"
echo "HTTPS (443):" && nc -z -w3 $SERVER_IP 443 && echo "✅ 开放" || echo "❌ 关闭"

# 快速HTTP测试
echo -e "\n🌐 快速HTTP测试..."
if curl -s --connect-timeout 5 --max-time 10 https://offerott.com/home | grep -q "html\|HTML"; then
    echo "✅ 网站响应正常"
else
    echo "❌ 网站无响应"
fi

echo -e "\n⏰ 如果服务器刚重启，可能需要等待2-5分钟完全启动" 