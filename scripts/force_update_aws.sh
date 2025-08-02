#!/bin/bash
# 强制更新AWS服务器脚本 - 解决OpenCV依赖问题
# 确保服务器获取最新代码并重新构建Docker镜像

set -e

AWS_SERVER="3.138.194.143"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"

echo "🚀 开始强制更新AWS服务器..."

# 1. 停止所有服务
echo "=== 1. 停止所有服务 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    echo "停止所有Docker服务..."
    docker-compose -f docker-compose.prod.yml down
    
    echo "清理所有Docker资源..."
    docker system prune -af
    docker volume prune -f
    
    echo "检查剩余容器..."
    docker ps -a
EOF

# 2. 强制更新代码
echo "=== 2. 强制更新代码 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    echo "当前Git状态:"
    git status
    
    echo "强制重置到最新版本..."
    git fetch origin
    git reset --hard origin/main
    git clean -fd
    
    echo "验证requirements.txt更新:"
    echo "检查opencv-python-headless配置..."
    if grep -n "opencv-python" backend/requirements.txt; then
        echo "✅ requirements.txt内容:"
        grep -A2 -B2 "opencv-python" backend/requirements.txt
    else
        echo "❌ 未找到opencv配置"
    fi
    
    echo "最新提交信息:"
    git log -1 --oneline
EOF

# 3. 强制重新构建后端
echo "=== 3. 强制重新构建后端 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    echo "开始强制重新构建后端镜像..."
    echo "构建命令: docker-compose -f docker-compose.prod.yml build --no-cache backend"
    
    # 使用timeout防止构建卡死
    timeout 1800 docker-compose -f docker-compose.prod.yml build --no-cache backend 2>&1 | while IFS= read -r line; do
        echo "[$(date '+%H:%M:%S')] $line"
        
        # 检查关键信息
        case "$line" in
            *"opencv-python-headless"*)
                echo "✅ 检测到正确的OpenCV headless版本安装"
                ;;
            *"opencv-python"*)
                echo "⚠️  检测到OpenCV相关安装: $line"
                ;;
            *"libGL"*|*"ERROR"*|*"FAILED"*)
                echo "❌ 检测到潜在错误: $line"
                ;;
            *"Successfully built"*)
                echo "✅ 构建成功: $line"
                ;;
        esac
    done
    
    build_result=$?
    if [ $build_result -eq 0 ]; then
        echo "✅ 后端镜像构建成功"
        
        echo "检查构建的镜像:"
        docker images | grep interviewpro
        
        echo "检查镜像中的OpenCV安装:"
        docker run --rm interviewpro-backend python -c "import cv2; print('OpenCV version:', cv2.__version__); print('OpenCV build info:', cv2.getBuildInformation()[:500])" || echo "⚠️  OpenCV测试失败"
        
    else
        echo "❌ 后端镜像构建失败"
        exit 1
    fi
EOF

# 4. 启动服务并监控
echo "=== 4. 启动服务并监控 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    echo "启动后端服务..."
    docker-compose -f docker-compose.prod.yml up -d backend
    
    echo "等待服务启动..."
    sleep 15
    
    echo "检查服务状态:"
    docker-compose -f docker-compose.prod.yml ps
    
    echo "检查启动日志:"
    docker-compose -f docker-compose.prod.yml logs --tail=50 backend
    
    # 检查是否还有OpenCV错误
    recent_logs=$(docker-compose -f docker-compose.prod.yml logs --tail=20 backend 2>&1)
    if echo "$recent_logs" | grep -q "libGL.so.1"; then
        echo "❌ 仍然存在OpenCV libGL错误"
        echo "错误日志:"
        echo "$recent_logs" | grep -A5 -B5 "libGL"
        exit 1
    elif echo "$recent_logs" | grep -q "Worker exiting"; then
        echo "❌ 检测到Worker退出"
        echo "$recent_logs" | grep -A3 -B3 "Worker"
        exit 1
    else
        echo "✅ 未检测到OpenCV相关错误"
    fi
EOF

echo ""
echo "🎉 强制更新完成!"
echo "📋 检查要点:"
echo "  1. 代码已强制更新到最新版本"
echo "  2. Docker镜像已强制重新构建"
echo "  3. 使用opencv-python-headless替代opencv-python"
echo "  4. 服务启动日志已检查"
echo ""
echo "🔗 测试地址: https://offerott.com" 