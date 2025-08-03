#!/bin/bash
# 分步部署脚本 - 处理SSH超时和长时间构建
# Usage: ./deploy_step_by_step.sh [step_number]

set -e

AWS_SERVER="3.138.194.143"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 颜色输出函数
red() { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
blue() { echo -e "\033[34m$1\033[0m"; }

# 获取步骤参数
STEP=${1:-1}

echo "🚀 $(blue '分步部署脚本') - 从步骤 $STEP 开始"

# 步骤1: 环境检查和代码更新
if [ $STEP -le 1 ]; then
    echo ""
    echo "=== $(yellow '步骤1: 环境检查和代码更新') ==="
    
    echo "检查SSH连接..."
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 "ec2-user@$AWS_SERVER" "echo 'SSH连接正常'" 2>/dev/null; then
        red "❌ SSH连接失败"
        exit 1
    fi
    green "✅ SSH连接正常"
    
    echo "停止现有服务并更新代码..."
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
        cd /home/ec2-user/InterviewPro
        
        echo "停止所有Docker服务..."
        docker-compose -f docker-compose.prod.yml down || true
        
        echo "清理Docker资源..."
        docker system prune -af
        docker volume prune -f
        
        echo "更新代码..."
        git fetch origin
        git reset --hard origin/main
        echo "当前提交: $(git log -1 --oneline)"
        
        echo "验证关键修复..."
        if grep -q "opencv-python-headless" backend/requirements.txt; then
            echo "✅ OpenCV headless配置正确"
        else
            echo "❌ OpenCV配置错误"
            exit 1
        fi
        
        if ! grep -q "pyaudio" backend/requirements.txt; then
            echo "✅ pyaudio已移除"
        else
            echo "❌ pyaudio仍然存在"
            exit 1
        fi
        
        if grep -q "libgl1-mesa-glx" backend/Dockerfile.prod; then
            echo "✅ Dockerfile系统依赖已添加"
        else
            echo "❌ Dockerfile系统依赖缺失"
            exit 1
        fi
EOF
    
    green "✅ 步骤1完成"
    echo ""
    echo "$(blue '下一步：运行') ./scripts/deploy_step_by_step.sh 2"
fi

# 步骤2: 构建Docker镜像
if [ $STEP -le 2 ]; then
    echo ""
    echo "=== $(yellow '步骤2: 构建Docker镜像') ==="
    
    echo "开始构建（这可能需要5-10分钟）..."
    
    # 使用nohup在后台运行构建，避免SSH超时
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
        cd /home/ec2-user/InterviewPro
        
        echo "开始后台构建Docker镜像..."
        nohup docker-compose -f docker-compose.prod.yml build --no-cache --progress=plain > build.log 2>&1 &
        BUILD_PID=$!
        echo "构建进程ID: $BUILD_PID"
        echo $BUILD_PID > build.pid
        
        echo "构建已在后台启动，日志文件: build.log"
        echo "您可以运行以下命令监控构建进度："
        echo "  ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 'cd /home/ec2-user/InterviewPro && tail -f build.log'"
EOF
    
    green "✅ 步骤2启动完成"
    echo ""
    echo "$(yellow '构建正在后台进行...')"
    echo "$(blue '监控构建：') ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 'cd /home/ec2-user/InterviewPro && tail -f build.log'"
    echo "$(blue '下一步：等待构建完成后运行') ./scripts/deploy_step_by_step.sh 3"
fi

# 步骤3: 检查构建状态
if [ $STEP -le 3 ]; then
    echo ""
    echo "=== $(yellow '步骤3: 检查构建状态') ==="
    
    BUILD_STATUS=$(ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
        cd /home/ec2-user/InterviewPro
        
        if [ -f build.pid ]; then
            BUILD_PID=$(cat build.pid)
            if kill -0 $BUILD_PID 2>/dev/null; then
                echo "RUNNING"
            else
                # 检查构建结果
                if tail -10 build.log | grep -q "Successfully built"; then
                    echo "SUCCESS"
                else
                    echo "FAILED"
                fi
            fi
        else
            echo "NO_BUILD"
        fi
EOF
    )
    
    case $BUILD_STATUS in
        "RUNNING")
            yellow "⏳ 构建仍在进行中..."
            echo "$(blue '监控构建：') ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 'cd /home/ec2-user/InterviewPro && tail -f build.log'"
            echo "$(blue '稍后再次检查：') ./scripts/deploy_step_by_step.sh 3"
            ;;
        "SUCCESS")
            green "✅ 构建成功完成"
            echo ""
            echo "$(blue '下一步：运行') ./scripts/deploy_step_by_step.sh 4"
            ;;
        "FAILED")
            red "❌ 构建失败"
            echo "$(blue '查看错误日志：') ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 'cd /home/ec2-user/InterviewPro && tail -50 build.log'"
            exit 1
            ;;
        "NO_BUILD")
            red "❌ 未找到构建进程"
            echo "$(blue '重新开始构建：') ./scripts/deploy_step_by_step.sh 2"
            exit 1
            ;;
    esac
fi

# 步骤4: 启动服务
if [ $STEP -le 4 ]; then
    echo ""
    echo "=== $(yellow '步骤4: 启动服务') ==="
    
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
        cd /home/ec2-user/InterviewPro
        
        echo "启动所有服务..."
        docker-compose -f docker-compose.prod.yml up -d
        
        echo "等待服务启动..."
        sleep 15
        
        echo "检查服务状态..."
        docker-compose -f docker-compose.prod.yml ps
        
        echo ""
        echo "检查后端服务日志..."
        docker-compose -f docker-compose.prod.yml logs --tail=20 backend
EOF
    
    green "✅ 步骤4完成"
    echo ""
    echo "$(blue '下一步：运行') ./scripts/deploy_step_by_step.sh 5"
fi

# 步骤5: 健康检查
if [ $STEP -le 5 ]; then
    echo ""
    echo "=== $(yellow '步骤5: 健康检查') ==="
    
    for i in {1..5}; do
        echo "第 $i 次健康检查..."
        
        if ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" "curl -f http://localhost:5001/api/v1/health" 2>/dev/null; then
            green "✅ 健康检查通过"
            break
        else
            if [ $i -eq 5 ]; then
                red "❌ 健康检查失败"
                echo "$(blue '查看服务日志：') ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 'cd /home/ec2-user/InterviewPro && docker-compose -f docker-compose.prod.yml logs backend'"
                exit 1
            else
                echo "等待服务完全启动..."
                sleep 10
            fi
        fi
    done
    
    # 最终状态检查
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
        cd /home/ec2-user/InterviewPro
        
        echo ""
        echo "=== 最终服务状态 ==="
        docker-compose -f docker-compose.prod.yml ps
        
        echo ""
        echo "=== 系统资源状态 ==="
        echo "磁盘使用："
        df -h | head -2
        echo "内存使用："
        free -h
        
        echo ""
        echo "=== 网络端口检查 ==="
        netstat -tlnp | grep -E "(80|443|5001|3306|6379)" | head -5
EOF
    
    green "🎉 部署完成！"
    echo ""
    echo "$(blue '访问地址:')"
    echo "  - HTTPS: https://offerott.com"
    echo "  - HTTP:  http://offerott.com (自动重定向到HTTPS)"
    echo ""
    echo "$(blue '如果遇到问题，查看日志：')"
    echo "  ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 'cd /home/ec2-user/InterviewPro && docker-compose -f docker-compose.prod.yml logs backend'"
fi 