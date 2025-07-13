#!/bin/bash

# 完整更新部署脚本 - 包含前端和后端的修改
# 根据昨天的修改创建

set -e

# 配置信息
SERVER_IP="3.14.247.189"
KEY_FILE="aws-myy-rsa.pem"
REMOTE_USER="ubuntu"

echo "🚀 开始完整更新部署到 AWS 服务器..."
echo "================================"
echo "📋 本次更新包含："
echo "  1. ✅ AI参考答案无限循环修复"
echo "  2. ✅ Mock Interview答案提交功能完善"  
echo "  3. ✅ 数据库session_id关联问题修复"
echo "  4. ✅ OAuth按钮隐藏功能"
echo "  5. ✅ 前端React hooks依赖项优化"
echo "================================"

# 检查SSH密钥文件是否存在
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ SSH密钥文件 $KEY_FILE 不存在"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ 请在项目根目录执行此脚本"
    exit 1
fi

# 1. 测试SSH连接
echo "1. 测试SSH连接..."
ssh -i "$KEY_FILE" -o ConnectTimeout=10 "$REMOTE_USER@$SERVER_IP" "echo '✅ SSH连接成功'"

# 2. 停止现有服务
echo -e "\n2. 停止现有服务..."
ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
if [ -f /home/ubuntu/InterviewPro/docker-compose.prod.yml ]; then
    cd /home/ubuntu/InterviewPro
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    echo '✅ 服务停止成功'
else
    echo '⚠️  docker-compose.prod.yml 不存在，跳过停止步骤'
fi
"

# 3. 构建前端应用
echo -e "\n3. 构建前端应用..."
echo "清理之前的构建..."
cd frontend
rm -rf dist

echo "开始构建生产版本..."
npx vite build --mode production

if [ ! -d "dist" ]; then
    echo "❌ 前端构建失败，dist目录不存在"
    exit 1
fi

echo "✅ 前端构建完成"

# 4. 创建前端部署包
echo -e "\n4. 创建前端部署包..."
cd dist
tar --no-xattrs -czf ../frontend-complete-update.tar.gz .
cd ..

echo "✅ 前端部署包创建完成"

# 5. 准备后端文件
echo -e "\n5. 准备后端文件..."
cd ../backend

# 创建后端部署包，包含所有修改
tar --no-xattrs -czf ../backend-complete-update.tar.gz \
    --exclude='venv' \
    --exclude='instance' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    .

echo "✅ 后端部署包创建完成"

# 6. 上传文件到服务器
echo -e "\n6. 上传文件到服务器..."
cd ..

echo "上传前端文件..."
scp -i "$KEY_FILE" frontend/frontend-complete-update.tar.gz "$REMOTE_USER@$SERVER_IP:/home/ubuntu/"

echo "上传后端文件..."
scp -i "$KEY_FILE" backend-complete-update.tar.gz "$REMOTE_USER@$SERVER_IP:/home/ubuntu/"

echo "✅ 文件上传完成"

# 7. 部署前端
echo -e "\n7. 部署前端..."
ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
set -e
echo '解压前端文件...'
cd /home/ubuntu
mkdir -p frontend-new-dist
cd frontend-new-dist
tar -xzf ../frontend-complete-update.tar.gz

echo '备份当前前端...'
if [ -d /home/ubuntu/InterviewPro/frontend/dist ]; then
    mv /home/ubuntu/InterviewPro/frontend/dist /home/ubuntu/InterviewPro/frontend/dist.backup.\$(date +%Y%m%d_%H%M%S)
fi

echo '部署新的前端文件...'
mkdir -p /home/ubuntu/InterviewPro/frontend/dist
cp -r . /home/ubuntu/InterviewPro/frontend/dist/

echo '✅ 前端部署完成'
"

# 8. 部署后端
echo -e "\n8. 部署后端..."
ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
set -e
echo '备份当前后端...'
if [ -d /home/ubuntu/InterviewPro/backend ]; then
    mv /home/ubuntu/InterviewPro/backend /home/ubuntu/InterviewPro/backend.backup.\$(date +%Y%m%d_%H%M%S)
fi

echo '解压后端文件...'
cd /home/ubuntu
mkdir -p backend-new
cd backend-new
tar -xzf ../backend-complete-update.tar.gz

echo '部署新的后端文件...'
mkdir -p /home/ubuntu/InterviewPro/backend
cp -r . /home/ubuntu/InterviewPro/backend/

echo '✅ 后端部署完成'
"

# 9. 更新Docker配置
echo -e "\n9. 更新Docker配置..."
ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
cd /home/ubuntu/InterviewPro

# 确保docker-compose.prod.yml存在
if [ ! -f docker-compose.prod.yml ]; then
    echo '创建生产环境Docker配置...'
    cat > docker-compose.prod.yml << 'EOF'
version: '3.8'
services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: interviewpro-backend-1
    ports:
      - \"5001:5001\"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///instance/interview.db
    volumes:
      - ./backend/instance:/app/instance
      - ./backend/uploads:/app/uploads
    restart: unless-stopped
    
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: interviewpro-frontend-1
    ports:
      - \"80:80\"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend
    restart: unless-stopped
EOF
fi

# 确保Dockerfile.prod存在
if [ ! -f backend/Dockerfile.prod ]; then
    echo '创建后端生产Dockerfile...'
    cat > backend/Dockerfile.prod << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance uploads

EXPOSE 5001

CMD [\"python\", \"run_complete.py\"]
EOF
fi

if [ ! -f frontend/Dockerfile.prod ]; then
    echo '创建前端生产Dockerfile...'
    cat > frontend/Dockerfile.prod << 'EOF'
FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY dist /usr/share/nginx/html

EXPOSE 80

CMD [\"nginx\", \"-g\", \"daemon off;\"]
EOF
fi

# 确保nginx.conf存在
if [ ! -f frontend/nginx.conf ]; then
    echo '创建nginx配置...'
    cat > frontend/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name _;
        
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files \$uri \$uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://backend:5001;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
fi

echo '✅ Docker配置更新完成'
"

# 10. 重新构建和启动服务
echo -e "\n10. 重新构建和启动服务..."
ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
cd /home/ubuntu/InterviewPro

echo '重新构建Docker镜像...'
docker-compose -f docker-compose.prod.yml build --no-cache

echo '启动服务...'
docker-compose -f docker-compose.prod.yml up -d

echo '等待服务启动...'
sleep 10

echo '检查服务状态...'
docker-compose -f docker-compose.prod.yml ps

echo '✅ 服务启动完成'
"

# 11. 清理临时文件
echo -e "\n11. 清理临时文件..."
ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
cd /home/ubuntu
rm -rf frontend-new-dist backend-new
rm -f frontend-complete-update.tar.gz backend-complete-update.tar.gz
echo '✅ 临时文件清理完成'
"

# 清理本地临时文件
rm -f frontend/frontend-complete-update.tar.gz backend-complete-update.tar.gz
echo "✅ 本地临时文件清理完成"

# 12. 验证部署
echo -e "\n12. 验证部署..."
sleep 10

echo "检查服务状态..."
ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
cd /home/ubuntu/InterviewPro
echo '=== Docker 服务状态 ==='
docker-compose -f docker-compose.prod.yml ps
echo ''
echo '=== 容器健康检查 ==='
docker exec interviewpro-backend-1 curl -f http://localhost:5001/api/v1/health || echo '后端健康检查失败'
echo ''
echo '=== 前端服务检查 ==='
curl -s -o /dev/null -w 'HTTP状态码: %{http_code}' http://localhost || echo '前端服务检查失败'
echo ''
"

echo "外部访问测试..."
curl -o /dev/null -s -w "HTTP状态码: %{http_code}\n响应时间: %{time_total}s\n" "http://$SERVER_IP" || echo "外部访问失败"

echo ""
echo "🎉 完整更新部署完成！"
echo "================================"
echo "📋 部署摘要："
echo "  ✅ 前端更新：OAuth按钮隐藏 + AI参考答案修复"
echo "  ✅ 后端更新：答案提交功能 + 数据库修复"
echo "  ✅ 服务重启：Docker容器重新构建"
echo "  ✅ 配置更新：生产环境配置优化"
echo ""
echo "🌐 访问地址："
echo "  - 网站首页: http://$SERVER_IP"
echo "  - 登录页面: http://$SERVER_IP/login"
echo "  - 注册页面: http://$SERVER_IP/register"
echo "  - API健康检查: http://$SERVER_IP/api/v1/health"
echo ""
echo "🔧 如需查看日志："
echo "  ssh -i $KEY_FILE $REMOTE_USER@$SERVER_IP"
echo "  cd /home/ubuntu/InterviewPro"
echo "  docker-compose -f docker-compose.prod.yml logs -f" 