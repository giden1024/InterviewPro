#!/bin/bash

# EC2实例状态检查脚本
SERVER_IP="3.144.27.91"

echo "🔍 检查EC2实例状态"
echo "================================"

# 如果有AWS CLI，检查实例状态
if command -v aws &> /dev/null; then
    echo "1. 查询EC2实例信息..."
    aws ec2 describe-instances \
        --filters "Name=ip-address,Values=$SERVER_IP" \
        --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress,SecurityGroups[*].GroupId]' \
        --output table
    
    echo -e "\n2. 检查安全组规则..."
    INSTANCE_ID=$(aws ec2 describe-instances \
        --filters "Name=ip-address,Values=$SERVER_IP" \
        --query 'Reservations[*].Instances[*].InstanceId' \
        --output text)
    
    if [ ! -z "$INSTANCE_ID" ]; then
        echo "实例ID: $INSTANCE_ID"
        
        # 获取安全组ID
        SECURITY_GROUPS=$(aws ec2 describe-instances \
            --instance-ids $INSTANCE_ID \
            --query 'Reservations[*].Instances[*].SecurityGroups[*].GroupId' \
            --output text)
        
        echo "安全组: $SECURITY_GROUPS"
        
        # 检查安全组规则
        for sg in $SECURITY_GROUPS; do
            echo -e "\n安全组 $sg 的入站规则:"
            aws ec2 describe-security-groups \
                --group-ids $sg \
                --query 'SecurityGroups[*].IpPermissions[*].[IpProtocol,FromPort,ToPort,IpRanges[*].CidrIp]' \
                --output table
        done
    else
        echo "❌ 未找到IP为 $SERVER_IP 的实例"
    fi
else
    echo "❌ AWS CLI未安装，请手动检查AWS控制台"
fi

echo -e "\n📋 手动检查步骤："
echo "1. 登录AWS控制台 -> EC2"
echo "2. 检查实例状态是否为 'running'"
echo "3. 检查实例是否有公网IP"
echo "4. 检查安全组入站规则"
echo "5. 检查网络ACL设置"
echo "6. 检查VPC路由表" 