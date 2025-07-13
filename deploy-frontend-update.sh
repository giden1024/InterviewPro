#!/bin/bash

# 前端更新部署脚本 - 推送OAuth按钮隐藏的改动
# 根据用户的成功部署经验创建

set -e

# 配置信息
SERVER_IP="3.14.247.189"
KEY_FILE="aws-myy-rsa.pem"
REMOTE_USER="ubuntu"

echo "🚀 开始部署前端更新到 AWS 服务器..."
echo "================================"

# 检查SSH密钥文件是否存在
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ SSH密钥文件 $KEY_FILE 不存在"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -d "frontend" ]; then
    echo "❌ 请在项目根目录执行此脚本"
    exit 1
fi

# 1. 测试SSH连接
echo "1. 测试SSH连接..."
ssh -i "$KEY_FILE" -o ConnectTimeout=10 "$REMOTE_USER@$SERVER_IP" "echo '✅ SSH连接成功'"

# 2. 构建前端应用
echo -e "\n2. 构建前端应用..."
cd frontend
echo "清理之前的构建..."
rm -rf dist

echo "开始构建生产版本..."
npx vite build --mode production

if [ ! -d "dist" ]; then
    echo "❌ 构建失败，dist目录不存在"
    exit 1
fi

echo "✅ 前端构建完成"

# 3. 创建部署包
echo -e "\n3. 创建部署包..."
cd dist
tar --no-xattrs -czf ../frontend-dist-oauth-hidden.tar.gz .
cd ..

echo "✅ 部署包创建完成: frontend-dist-oauth-hidden.tar.gz"

# 4. 上传到服务器
echo -e "\n4. 上传到服务器..."
scp -i "../$KEY_FILE" frontend-dist-oauth-hidden.tar.gz "$REMOTE_USER@$SERVER_IP:/home/ubuntu/"

echo "✅ 文件上传完成"

# 5. 在服务器上部署
echo -e "\n5. 在服务器上部署..."
ssh -i "../$KEY_FILE" "$REMOTE_USER@$SERVER_IP" << 'EOF'
set -e

echo "解压新的前端文件..."
cd /home/ubuntu
mkdir -p frontend-new-dist
cd frontend-new-dist
tar -xzf ../frontend-dist-oauth-hidden.tar.gz

echo "将文件复制到前端容器..."
docker cp . interviewpro-frontend-1:/usr/share/nginx/html/

echo "重启前端容器..."
docker restart interviewpro-frontend-1

echo "清理临时文件..."
cd /home/ubuntu
rm -rf frontend-new-dist
rm -f frontend-dist-oauth-hidden.tar.gz

echo "✅ 服务器部署完成"
EOF

# 6. 验证部署
echo -e "\n6. 验证部署..."
sleep 5

# 检查服务状态
echo "检查Docker容器状态..."
ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "docker ps | grep interviewpro-frontend"

# 检查前端是否可访问
echo "检查前端访问..."
HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" "http://$SERVER_IP" || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 前端页面可正常访问"
else
    echo "⚠️ 前端访问返回状态码: $HTTP_CODE"
fi

# 清理本地文件
cd ..
rm -f frontend/frontend-dist-oauth-hidden.tar.gz

echo -e "\n🎉 部署完成！"
echo "================================"
echo "访问地址: http://$SERVER_IP"
echo "OAuth按钮已隐藏"
echo ""
echo "如需查看日志："
echo "ssh -i $KEY_FILE $REMOTE_USER@$SERVER_IP"
echo "docker logs interviewpro-frontend-1" 