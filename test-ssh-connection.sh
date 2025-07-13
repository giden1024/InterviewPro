#!/bin/bash

# SSH连接测试脚本
SERVER_IP="3.144.27.91"
KEY_FILE="/Users/mayuyang/InterviewPro/aws-myy-rsa.pem"

echo "🔍 测试SSH连接到AWS服务器: $SERVER_IP"
echo "使用密钥文件: $KEY_FILE"
echo "================================"

# 检查密钥文件
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ 密钥文件不存在: $KEY_FILE"
    exit 1
fi

echo "✅ 密钥文件存在"
echo "文件权限: $(ls -l $KEY_FILE | awk '{print $1}')"

# 测试不同的用户名
USERS=("ubuntu" "ec2-user" "admin" "root")

for user in "${USERS[@]}"; do
    echo -e "\n🔐 尝试连接用户: $user"
    echo "命令: ssh -i $KEY_FILE -o ConnectTimeout=10 -o StrictHostKeyChecking=no $user@$SERVER_IP"
    
    # 使用timeout命令限制连接时间
    if command -v gtimeout &> /dev/null; then
        TIMEOUT_CMD="gtimeout 15"
    else
        TIMEOUT_CMD="timeout 15"
    fi
    
    # 尝试连接
    $TIMEOUT_CMD ssh -i "$KEY_FILE" \
        -o ConnectTimeout=10 \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o LogLevel=ERROR \
        "$user@$SERVER_IP" \
        "echo 'SSH连接成功！用户: $user'; uname -a; exit" 2>&1
    
    result=$?
    if [ $result -eq 0 ]; then
        echo "✅ SSH连接成功！用户: $user"
        echo "🎉 可以使用以下命令连接服务器："
        echo "ssh -i $KEY_FILE $user@$SERVER_IP"
        break
    elif [ $result -eq 124 ]; then
        echo "❌ 连接超时"
    else
        echo "❌ 连接失败 (退出码: $result)"
    fi
done

echo -e "\n📋 如果所有连接都失败，请检查："
echo "1. EC2实例是否正在运行"
echo "2. 安全组是否允许SSH端口22"
echo "3. 密钥对是否与实例匹配"
echo "4. 网络ACL和路由表配置" 