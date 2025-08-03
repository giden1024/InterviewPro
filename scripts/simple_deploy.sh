#!/bin/bash
# 简化部署脚本 - 逐步执行

AWS_SERVER="3.138.194.143"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"

echo "🚀 开始简化部署流程..."

# 1. 更新代码
echo "=== 1. 更新代码 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    echo "获取最新代码..."
    git fetch origin
    git reset --hard origin/main
    echo "当前提交: $(git log -1 --oneline)"
    
    echo "验证requirements.txt..."
    if grep -q "opencv-python-headless" backend/requirements.txt; then
        echo "✅ OpenCV headless配置正确"
    else
        echo "❌ OpenCV配置错误"
        exit 1
    fi
    
    if [ $(grep -c "redis==" backend/requirements.txt) -eq 1 ]; then
        echo "✅ Redis版本唯一"
    else
        echo "❌ Redis版本冲突"
        grep "redis==" backend/requirements.txt
        exit 1
    fi
EOF

if [ $? -ne 0 ]; then
    echo "❌ 代码更新失败"
    exit 1
fi

# 2. 停止服务
echo "=== 2. 停止现有服务 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    docker-compose -f docker-compose.prod.yml down
    docker system prune -f
EOF

# 3. 构建后端
echo "=== 3. 构建后端镜像 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    echo "开始构建后端..."
    docker-compose -f docker-compose.prod.yml build --no-cache backend
    
    if [ $? -eq 0 ]; then
        echo "✅ 后端构建成功"
    else
        echo "❌ 后端构建失败"
        exit 1
    fi
EOF

if [ $? -ne 0 ]; then
    echo "❌ 后端构建失败"
    exit 1
fi

# 4. 启动服务
echo "=== 4. 启动所有服务 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    echo "启动所有服务..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "等待服务启动..."
    sleep 30
    
    echo "检查服务状态:"
    docker-compose -f docker-compose.prod.yml ps
EOF

# 5. 验证部署
echo "=== 5. 验证部署 ==="
sleep 10

ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    echo "检查端口监听:"
    netstat -tlnp | grep :5001
    
    echo "检查后端日志:"
    docker-compose -f docker-compose.prod.yml logs --tail=30 backend
    
    # 检查错误
    logs=$(docker-compose -f docker-compose.prod.yml logs backend 2>&1)
    if echo "$logs" | grep -q "libGL.so.1"; then
        echo "❌ OpenCV错误仍然存在"
        exit 1
    elif echo "$logs" | grep -q "Worker exiting"; then
        echo "❌ Worker退出错误"
        exit 1
    else
        echo "✅ 没有检测到OpenCV错误"
    fi
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 部署成功完成!"
    echo "🔗 网站地址: https://offerott.com"
    echo ""
    echo "📊 解决的问题:"
    echo "  ✅ OpenCV依赖问题 (使用headless版本)"
    echo "  ✅ Redis版本冲突问题"
    echo "  ✅ Dockerfile重复依赖问题"
else
    echo "❌ 部署验证失败"
    exit 1
fi 