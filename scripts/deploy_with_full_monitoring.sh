#!/bin/bash
# 完整部署监控脚本 v2.0 - 实时日志监控和错误检测
# 解决OpenCV问题并实现全程监控

set -e

# 配置变量
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="logs/deployment"
LOG_FILE="$LOG_DIR/deploy_$TIMESTAMP.log"
ERROR_LOG="$LOG_DIR/error_$TIMESTAMP.log"
AWS_SERVER="3.138.194.143"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 颜色输出函数
red() { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
blue() { echo -e "\033[34m$1\033[0m"; }

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

error_log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: $1" | tee -a "$ERROR_LOG" >&2
}

# 错误处理函数
handle_error() {
    local exit_code=$?
    error_log "部署失败，退出码: $exit_code"
    error_log "检查日志文件: $LOG_FILE 和 $ERROR_LOG"
    exit $exit_code
}

trap handle_error ERR

echo "🚀 $(blue '开始完整部署流程'): $(date)"
echo "📋 $(blue '日志文件'): $LOG_FILE"
echo "❌ $(blue '错误日志'): $ERROR_LOG"

# 1. 环境检查
log "=== 1. 环境检查 ==="
echo "检查SSH连接..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 "ec2-user@$AWS_SERVER" "echo 'SSH连接正常'" 2>/dev/null; then
    error_log "SSH连接失败"
    exit 1
fi
green "✅ SSH连接正常"

# 2. 停止现有服务
log "=== 2. 停止现有服务 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    echo "停止所有Docker服务..."
    docker-compose -f docker-compose.prod.yml down || true
    
    echo "清理Docker资源..."
    docker system prune -af
    docker volume prune -f
EOF
green "✅ 服务停止完成"

# 3. 更新代码
log "=== 3. 更新代码 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    echo "获取最新代码..."
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
green "✅ 代码更新完成"

# 4. 构建服务（带实时日志监控）
log "=== 4. 构建服务 ==="
echo "$(yellow '开始构建Docker镜像...')"

# 创建远程构建脚本，包含实时日志输出
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    echo "开始构建..."
    # 使用 --no-cache 确保完全重新构建
    docker-compose -f docker-compose.prod.yml build --no-cache --progress=plain 2>&1 | while IFS= read -r line; do
        echo "$(date '+%H:%M:%S') BUILD: $line"
        
        # 检测关键错误
        if echo "$line" | grep -q "libGL.so.1"; then
            echo "❌ 检测到OpenCV错误: $line"
        elif echo "$line" | grep -q "portaudio.h"; then
            echo "❌ 检测到portaudio错误: $line"
        elif echo "$line" | grep -q "No space left"; then
            echo "❌ 检测到磁盘空间不足: $line"
        elif echo "$line" | grep -q "Successfully built"; then
            echo "✅ 构建成功: $line"
        elif echo "$line" | grep -q "ERROR"; then
            echo "❌ 构建错误: $line"
        fi
    done
    
    # 检查构建结果
    if [ $? -eq 0 ]; then
        echo "✅ Docker镜像构建成功"
    else
        echo "❌ Docker镜像构建失败"
        exit 1
    fi
EOF

if [ $? -eq 0 ]; then
    green "✅ 构建完成"
else
    red "❌ 构建失败"
    exit 1
fi

# 5. 启动服务（带实时监控）
log "=== 5. 启动服务 ==="
echo "$(yellow '启动所有服务...')"

ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    echo "启动服务..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "等待服务启动..."
    sleep 10
    
    echo "检查服务状态..."
    docker-compose -f docker-compose.prod.yml ps
    
    echo "检查后端服务日志..."
    timeout 30 docker-compose -f docker-compose.prod.yml logs --tail=50 backend | while IFS= read -r line; do
        echo "$(date '+%H:%M:%S') BACKEND: $line"
        
        # 检测关键错误和成功信息
        if echo "$line" | grep -q "libGL.so.1"; then
            echo "❌ 仍然存在OpenCV错误: $line"
            exit 1
        elif echo "$line" | grep -q "Worker exiting"; then
            echo "❌ 检测到Worker退出: $line"
            exit 1
        elif echo "$line" | grep -q "Listening at"; then
            echo "✅ 服务启动成功: $line"
        elif echo "$line" | grep -q "Booting worker"; then
            echo "✅ Worker启动: $line"
        fi
    done
EOF

if [ $? -eq 0 ]; then
    green "✅ 服务启动成功"
else
    red "❌ 服务启动失败"
    exit 1
fi

# 6. 健康检查
log "=== 6. 健康检查 ==="
echo "$(yellow '执行健康检查...')"

for i in {1..5}; do
    echo "第 $i 次健康检查..."
    
    if ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" "curl -f http://localhost:5001/api/v1/health" 2>/dev/null; then
        green "✅ 健康检查通过"
        break
    else
        if [ $i -eq 5 ]; then
            red "❌ 健康检查失败"
            exit 1
        else
            echo "等待服务完全启动..."
            sleep 10
        fi
    fi
done

# 7. 最终状态检查
log "=== 7. 最终状态检查 ==="
ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    cd /home/ec2-user/InterviewPro
    
    echo "=== 最终服务状态 ==="
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "=== 磁盘使用情况 ==="
    df -h
    
    echo ""
    echo "=== 内存使用情况 ==="
    free -h
    
    echo ""
    echo "=== 网络端口检查 ==="
    netstat -tlnp | grep -E "(80|443|5001|3306|6379)"
EOF

green "🎉 部署完成！"
log "部署成功完成于: $(date)"
echo ""
echo "$(blue '访问地址:')"
echo "  - HTTPS: https://offerott.com"
echo "  - HTTP:  http://offerott.com (自动重定向到HTTPS)"
echo ""
echo "$(blue '日志文件:')"
echo "  - 部署日志: $LOG_FILE"
echo "  - 错误日志: $ERROR_LOG" 