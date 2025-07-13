#!/bin/bash

# AWS服务器连接测试
SERVER_IP="3.144.27.91"

echo "🔍 测试AWS服务器连接: $SERVER_IP"
echo "================================"

# 测试SSH端口
echo "1. 测试SSH端口 (22)..."
timeout 10 nc -zv $SERVER_IP 22 2>&1
if [ $? -eq 0 ]; then
    echo "✅ SSH端口可访问"
else
    echo "❌ SSH端口不可访问"
fi

# 测试HTTP端口
echo -e "\n2. 测试HTTP端口 (80)..."
timeout 10 nc -zv $SERVER_IP 80 2>&1
if [ $? -eq 0 ]; then
    echo "✅ HTTP端口可访问"
else
    echo "❌ HTTP端口不可访问"
fi

# 测试HTTPS端口
echo -e "\n3. 测试HTTPS端口 (443)..."
timeout 10 nc -zv $SERVER_IP 443 2>&1
if [ $? -eq 0 ]; then
    echo "✅ HTTPS端口可访问"
else
    echo "❌ HTTPS端口不可访问"
fi

# 测试API端口
echo -e "\n4. 测试API端口 (5001)..."
timeout 10 nc -zv $SERVER_IP 5001 2>&1
if [ $? -eq 0 ]; then
    echo "✅ API端口可访问"
else
    echo "❌ API端口不可访问"
fi

echo -e "\n📋 下一步操作建议："
echo "1. 如果SSH端口可访问，请使用以下命令连接："
echo "   ssh -i your-key.pem ubuntu@$SERVER_IP"
echo "2. 如果所有端口都不可访问，请检查AWS安全组配置"
echo "3. 确保EC2实例正在运行状态" 