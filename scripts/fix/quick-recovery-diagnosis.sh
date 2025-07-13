#!/bin/bash

echo "🚨 InterviewPro生产服务器紧急诊断和恢复"
echo "时间: $(date)"
echo "=========================================="

SERVER_IP="3.14.247.189"
KEY_PATH="~/.ssh/aws-myy-rsa.pem"

echo "📍 1. 基础网络连通性测试..."
echo "Ping测试:"
if ping -c 3 $SERVER_IP; then
    echo "✅ Ping正常"
else
    echo "❌ Ping失败 - 服务器可能完全停机"
fi

echo -e "\n🔌 2. 端口连通性测试..."
echo "测试HTTPS端口443:"
if nc -z -w5 $SERVER_IP 443; then
    echo "✅ HTTPS端口可达"
else
    echo "❌ HTTPS端口不可达"
fi

echo "测试SSH端口22:"
if nc -z -w5 $SERVER_IP 22; then
    echo "✅ SSH端口可达"
else
    echo "❌ SSH端口不可达"
fi

echo "测试HTTP端口80:"
if nc -z -w5 $SERVER_IP 80; then
    echo "✅ HTTP端口可达"
else
    echo "❌ HTTP端口不可达"
fi

echo -e "\n🌐 3. HTTP/HTTPS响应测试..."
echo "测试网站首页:"
if curl -I --connect-timeout 10 --max-time 15 https://offerott.com 2>/dev/null | grep -q "HTTP"; then
    echo "✅ HTTPS响应正常"
    curl -I --connect-timeout 5 https://offerott.com 2>/dev/null | head -3
else
    echo "❌ HTTPS无响应"
fi

echo -e "\n🔧 4. SSH连接测试..."
echo "尝试SSH连接:"
ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/aws-myy-rsa.pem ubuntu@$SERVER_IP "echo 'SSH连接成功'; date; uptime" 2>/dev/null && echo "✅ SSH连接正常" || echo "❌ SSH连接失败"

echo -e "\n📊 5. 诊断结果总结:"
echo "如果所有测试都失败，可能的原因："
echo "1. EC2实例已停止运行"
echo "2. 安全组配置问题"
echo "3. 网络ACL问题"
echo "4. AWS区域性故障"
echo "5. 我的重新部署操作导致系统崩溃"

echo -e "\n💡 6. 建议的恢复步骤:"
echo "1. 检查AWS控制台中EC2实例状态"
echo "2. 如果实例停止，尝试启动"
echo "3. 检查安全组设置"
echo "4. 如果实例无法启动，考虑从备份恢复"
echo "5. 最坏情况：重新部署整个应用"

echo -e "\n🆘 如果需要重新启动EC2实例，可以运行:"
echo "aws ec2 start-instances --instance-ids <instance-id>"

echo -e "\n✅ 诊断完成" 