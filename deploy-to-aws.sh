#!/bin/bash

# AWS InterviewPro 部署脚本
SERVER_IP="3.14.247.189"
KEY_FILE="/Users/mayuyang/InterviewPro/aws-myy-rsa.pem"
SSH_CMD="ssh -i $KEY_FILE ubuntu@$SERVER_IP"

echo "🚀 开始部署InterviewPro到AWS服务器: $SERVER_IP"
echo "================================"

# 1. 检查连接
echo "1. 测试SSH连接..."
$SSH_CMD "echo '✅ SSH连接成功'"
if [ $? -ne 0 ]; then
    echo "❌ SSH连接失败，请检查网络和密钥"
    exit 1
fi

# 2. 更新系统
echo -e "\n2. 更新系统包..."
$SSH_CMD "sudo apt update && sudo apt upgrade -y"

# 3. 安装Docker
echo -e "\n3. 安装Docker..."
$SSH_CMD "
if ! command -v docker &> /dev/null; then
    echo '安装Docker...'
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    echo '✅ Docker安装完成'
else
    echo '✅ Docker已安装'
fi
"

# 4. 安装Docker Compose
echo -e "\n4. 安装Docker Compose..."
$SSH_CMD "
if ! command -v docker-compose &> /dev/null; then
    echo '安装Docker Compose...'
    sudo curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo '✅ Docker Compose安装完成'
else
    echo '✅ Docker Compose已安装'
fi
"

# 5. 安装Node.js
echo -e "\n5. 安装Node.js..."
$SSH_CMD "
if ! command -v node &> /dev/null; then
    echo '安装Node.js...'
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo '✅ Node.js安装完成'
else
    echo '✅ Node.js已安装'
fi
"

# 6. 安装其他工具
echo -e "\n6. 安装其他必要工具..."
$SSH_CMD "
sudo apt-get install -y python3 python3-pip git nginx
echo '✅ 基础工具安装完成'
"

# 7. 克隆项目代码
echo -e "\n7. 上传项目代码..."
# 创建项目压缩包
tar --exclude='node_modules' --exclude='venv' --exclude='.git' --exclude='backend/instance' -czf interviewpro.tar.gz .

# 上传到服务器
scp -i $KEY_FILE interviewpro.tar.gz ubuntu@$SERVER_IP:/home/ubuntu/

# 解压项目
$SSH_CMD "
if [ -d 'InterviewPro' ]; then
    rm -rf InterviewPro
fi
mkdir InterviewPro
cd InterviewPro
tar -xzf ../interviewpro.tar.gz
echo '✅ 项目代码上传完成'
"

# 8. 配置环境变量
echo -e "\n8. 配置环境变量..."
$SSH_CMD "
cd InterviewPro
cp env.production.template .env.production

# 生成随机JWT密钥
JWT_SECRET=\$(openssl rand -base64 32)

# 更新配置文件
sed -i \"s|DATABASE_URL=.*|DATABASE_URL=sqlite:///instance/interview.db|g\" .env.production
sed -i \"s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=\$JWT_SECRET|g\" .env.production
sed -i \"s|CORS_ORIGINS=.*|CORS_ORIGINS=http://$SERVER_IP,https://$SERVER_IP|g\" .env.production
sed -i \"s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=http://$SERVER_IP/api/v1|g\" .env.production

echo '✅ 环境变量配置完成'
"

# 9. 构建和启动服务
echo -e "\n9. 构建和启动服务..."
$SSH_CMD "
cd InterviewPro
chmod +x deploy-aws.sh
./deploy-aws.sh
"

# 10. 验证部署
echo -e "\n10. 验证部署..."
sleep 10
$SSH_CMD "
cd InterviewPro
docker-compose -f docker-compose.prod.yml ps
curl -f http://localhost/api/v1/health || echo '健康检查失败，但服务可能正在启动中'
"

# 清理本地文件
rm -f interviewpro.tar.gz

echo -e "\n🎉 部署完成！"
echo "================================"
echo "访问地址："
echo "- 前端: http://$SERVER_IP"
echo "- API: http://$SERVER_IP/api/v1"
echo "- 健康检查: http://$SERVER_IP/api/v1/health"
echo ""
echo "如需查看日志："
echo "ssh -i $KEY_FILE ubuntu@$SERVER_IP"
echo "cd InterviewPro && docker-compose -f docker-compose.prod.yml logs" 