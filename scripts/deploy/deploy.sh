#!/bin/bash

echo "🚀 开始部署InterviewPro到生产服务器..."

# 服务器信息
SERVER_IP="47.110.144.20"
SERVER_USER="root"
PROJECT_NAME="interviewpro"

echo "📦 准备部署文件..."

# 创建部署目录
mkdir -p deploy

# 复制必要文件到部署目录
cp Dockerfile.frontend deploy/
cp Dockerfile.backend deploy/
cp docker-compose.prod.yml deploy/
cp nginx.prod.conf deploy/
cp nginx.conf deploy/

# 复制项目文件
cp -r frontend deploy/
cp -r backend deploy/

echo "📤 上传文件到服务器..."

# 使用scp上传文件
scp -r deploy/ ${SERVER_USER}@${SERVER_IP}:/tmp/

echo "🔧 在服务器上执行部署..."

# SSH到服务器执行部署命令
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
    # 移动文件到项目目录
    mkdir -p /opt/interviewpro
    cp -r /tmp/deploy/* /opt/interviewpro/
    cd /opt/interviewpro
    
    # 停止现有服务
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # 清理旧镜像
    docker system prune -f
    
    # 构建和启动服务
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
    
    # 显示运行状态
    docker-compose -f docker-compose.prod.yml ps
    
    echo "✅ 部署完成！"
    echo "🌐 访问地址: http://47.110.144.20"
    echo "🔗 域名访问: http://offerott.com (需要DNS解析)"
EOF

echo "🎉 部署脚本执行完成！" 