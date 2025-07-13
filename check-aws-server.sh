#!/bin/bash

# AWS服务器检查脚本
SERVER_IP="3.144.27.91"

echo "🔍 检查AWS服务器状态: $SERVER_IP"
echo "================================"

echo "1. 网络连通性测试..."
if ping -c 3 $SERVER_IP > /dev/null 2>&1; then
    echo "✅ Ping测试: 成功"
else
    echo "❌ Ping测试: 失败"
fi

echo ""
echo "2. 端口连通性测试..."

# 测试常用端口
ports=(22 80 443 5001)
for port in "${ports[@]}"; do
    if nc -z -w5 $SERVER_IP $port 2>/dev/null; then
        echo "✅ 端口 $port: 开放"
    else
        echo "❌ 端口 $port: 关闭或被阻止"
    fi
done

echo ""
echo "3. HTTP服务测试..."
if curl -I --connect-timeout 10 http://$SERVER_IP 2>/dev/null | head -1; then
    echo "✅ HTTP服务: 可访问"
else
    echo "❌ HTTP服务: 无法访问"
fi

echo ""
echo "4. 建议的解决方案:"
echo "   - 检查AWS安全组设置"
echo "   - 确认EC2实例运行状态"
echo "   - 检查服务器防火墙配置"
echo "   - 验证应用程序是否正在运行"

echo ""
echo "5. 如果有AWS CLI，可以运行以下命令检查："
echo "   aws ec2 describe-instances --filters \"Name=ip-address,Values=$SERVER_IP\""
echo "   aws ec2 describe-security-groups" 