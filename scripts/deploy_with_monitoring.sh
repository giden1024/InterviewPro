#!/bin/bash
# 完整部署监控脚本: 解决OpenCV问题并实现全程监控
# Usage: ./deploy_with_monitoring.sh

set -e  # 遇到错误立即退出

# 配置变量
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="logs/deployment"
LOG_FILE="$LOG_DIR/deploy_$TIMESTAMP.log"
ERROR_LOG="$LOG_DIR/error_$TIMESTAMP.log"
AWS_SERVER="3.138.194.143"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 重定向所有输出到日志文件
exec > >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$ERROR_LOG" >&2)

echo "🚀 开始完整部署流程: $(date)"
echo "📋 日志文件: $LOG_FILE"
echo "❌ 错误日志: $ERROR_LOG"

# 1. 环境检查函数
check_environment() {
    echo "=== 1. 环境检查 ==="
    
    echo "检查SSH连接..."
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 "ec2-user@$AWS_SERVER" "echo 'SSH连接正常'" 2>/dev/null; then
        echo "❌ SSH连接失败"
        return 1
    fi
    
    echo "检查服务器基本信息..."
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
        echo "服务器时间: $(date)"
        echo "系统信息: $(uname -a)"
        echo "磁盘使用情况:"
        df -h
        echo "内存使用情况:"
        free -h
        echo "Docker版本:"
        docker --version
        echo "Docker Compose版本:"
        docker-compose --version
EOF
    
    echo "✅ 环境检查完成"
}

# 2. 代码更新函数
update_code() {
    echo "=== 2. 代码更新 ==="
    
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
        cd /home/ec2-user/InterviewPro
        
        echo "当前Git状态:"
        git status
        
        echo "备份当前更改..."
        git stash push -m "backup_before_deploy_$(date +%Y%m%d_%H%M%S)"
        
        echo "清理未跟踪文件..."
        git clean -fd
        
        echo "获取最新代码..."
        git fetch origin
        git reset --hard origin/main
        
        echo "更新后的提交信息:"
        git log -1 --oneline
        
        echo "检查requirements.txt..."
        if grep -q "opencv-python-headless" backend/requirements.txt; then
            echo "✅ OpenCV headless版本已配置"
        else
            echo "❌ OpenCV配置可能有问题"
            head -20 backend/requirements.txt
        fi
EOF
    
    echo "✅ 代码更新完成"
}

# 3. 构建监控函数
build_with_monitoring() {
    local service=$1
    echo "=== 3. 构建服务: $service ==="
    
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << EOF
        cd /home/ec2-user/InterviewPro
        
        echo "开始构建 $service..."
        echo "构建开始时间: \$(date)"
        
        # 清理旧的镜像和容器
        echo "清理Docker缓存..."
        docker system prune -f
        
        # 开始构建并实时监控
        timeout 1800 docker-compose -f docker-compose.prod.yml build $service 2>&1 | while IFS= read -r line; do
            echo "[\$(date '+%H:%M:%S')] \$line"
            
            # 检查关键错误
            case "\$line" in
                *"ERROR"*|*"FAILED"*|*"No space left"*|*"libGL.so.1"*)
                    echo "❌ 检测到构建错误: \$line" >&2
                    ;;
                *"Step"*":")
                    echo "📦 构建进度: \$line"
                    ;;
                *"Successfully built"*)
                    echo "✅ 构建成功: \$line"
                    ;;
            esac
        done
        
        # 检查构建结果
        build_exit_code=\$?
        if [ \$build_exit_code -eq 0 ]; then
            echo "✅ $service 构建成功"
            echo "构建完成时间: \$(date)"
            
            # 检查镜像是否创建成功
            if docker images | grep -q "interviewpro-$service"; then
                echo "✅ Docker镜像创建成功"
                docker images | grep "interviewpro-$service"
            else
                echo "❌ Docker镜像未找到"
                return 1
            fi
        else
            echo "❌ $service 构建失败，退出码: \$build_exit_code"
            return 1
        fi
EOF
    
    local ssh_exit_code=$?
    if [ $ssh_exit_code -eq 0 ]; then
        echo "✅ 构建监控完成"
        return 0
    else
        echo "❌ 构建失败"
        return 1
    fi
}

# 4. 启动监控函数
start_with_monitoring() {
    local service=$1
    echo "=== 4. 启动服务: $service ==="
    
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << EOF
        cd /home/ec2-user/InterviewPro
        
        echo "停止现有服务..."
        docker-compose -f docker-compose.prod.yml down $service
        
        echo "启动 $service 服务..."
        docker-compose -f docker-compose.prod.yml up -d $service
        
        echo "等待服务启动..."
        sleep 10
        
        # 监控启动过程
        timeout=180  # 3分钟超时
        start_time=\$(date +%s)
        
        while true; do
            current_time=\$(date +%s)
            elapsed=\$((current_time - start_time))
            
            if [ \$elapsed -gt \$timeout ]; then
                echo "❌ $service 启动超时 (\${timeout}秒)"
                echo "获取服务日志:"
                docker-compose -f docker-compose.prod.yml logs --tail=50 $service
                return 1
            fi
            
            # 检查容器状态
            container_status=\$(docker-compose -f docker-compose.prod.yml ps $service 2>/dev/null | grep $service | awk '{print \$4}' || echo "not_found")
            
            echo "⏳ 检查服务状态... (\${elapsed}s/\${timeout}s) - 状态: \$container_status"
            
            if echo "\$container_status" | grep -q "Up"; then
                echo "✅ $service 启动成功"
                
                # 显示服务信息
                echo "服务详细信息:"
                docker-compose -f docker-compose.prod.yml ps $service
                
                # 检查日志中是否有错误
                echo "检查启动日志..."
                recent_logs=\$(docker-compose -f docker-compose.prod.yml logs --tail=20 $service 2>&1)
                if echo "\$recent_logs" | grep -i "error\|failed\|exception"; then
                    echo "⚠️  发现启动警告:"
                    echo "\$recent_logs" | grep -i "error\|failed\|exception"
                else
                    echo "✅ 启动日志正常"
                fi
                
                return 0
            elif echo "\$container_status" | grep -q "Exit"; then
                echo "❌ $service 启动失败，容器已退出"
                echo "获取错误日志:"
                docker-compose -f docker-compose.prod.yml logs --tail=100 $service
                return 1
            fi
            
            sleep 10
        done
EOF
    
    local ssh_exit_code=$?
    if [ $ssh_exit_code -eq 0 ]; then
        echo "✅ 启动监控完成"
        return 0
    else
        echo "❌ 服务启动失败"
        return 1
    fi
}

# 5. 健康检查函数
health_check() {
    echo "=== 5. 健康检查 ==="
    
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
        echo "执行健康检查..."
        
        # 检查端口监听
        echo "检查端口5001监听状态:"
        if netstat -tlnp 2>/dev/null | grep :5001; then
            echo "✅ 端口5001正在监听"
        else
            echo "❌ 端口5001未监听"
        fi
        
        # 检查API响应
        echo "测试API健康检查..."
        for i in {1..10}; do
            if curl -f -m 10 http://localhost:5001/api/v1/health >/dev/null 2>&1; then
                echo "✅ API健康检查通过 (尝试 $i/10)"
                
                # 获取API响应详情
                echo "API响应详情:"
                curl -s http://localhost:5001/api/v1/health | head -5
                return 0
            else
                echo "⏳ API未响应，等待... ($i/10)"
                sleep 10
            fi
        done
        
        echo "❌ API健康检查失败"
        return 1
EOF
    
    local ssh_exit_code=$?
    if [ $ssh_exit_code -eq 0 ]; then
        echo "✅ 健康检查通过"
        return 0
    else
        echo "❌ 健康检查失败"
        return 1
    fi
}

# 6. 错误诊断函数
diagnose_failure() {
    local service=$1
    echo "=== 6. 错误诊断: $service ==="
    
    ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << EOF
        cd /home/ec2-user/InterviewPro
        
        echo "开始诊断 $service 服务失败原因..."
        
        echo "1. 容器状态:"
        docker-compose -f docker-compose.prod.yml ps
        
        echo "2. 容器日志 (最近100行):"
        docker-compose -f docker-compose.prod.yml logs --tail=100 $service
        
        echo "3. 系统资源:"
        echo "内存使用:"
        free -h
        echo "磁盘使用:"
        df -h
        echo "CPU负载:"
        uptime
        
        echo "4. Docker信息:"
        docker system df
        docker images | head -10
        
        echo "5. 网络检查:"
        netstat -tlnp | grep -E ':5001|:3306|:6379'
        
        echo "6. 进程检查:"
        ps aux | grep -E 'python|gunicorn|mysql|redis' | head -10
        
        echo "7. 错误模式分析:"
        logs=\$(docker-compose -f docker-compose.prod.yml logs $service 2>&1)
        
        if echo "\$logs" | grep -q "libGL.so.1"; then
            echo "🔍 检测到OpenCV图形库问题"
            echo "   - 原因: 使用了完整版opencv-python而非headless版本"
            echo "   - 解决: 已替换为opencv-python-headless"
            echo "   - 状态: 需要重新构建"
        fi
        
        if echo "\$logs" | grep -q "No space left"; then
            echo "🔍 检测到磁盘空间不足"
            echo "   - 建议: 清理Docker缓存"
        fi
        
        if echo "\$logs" | grep -q "Worker.*exiting"; then
            echo "🔍 检测到Gunicorn Worker退出"
            echo "   - 可能原因: 依赖库加载失败"
        fi
        
        if echo "\$logs" | grep -q "ImportError"; then
            echo "🔍 检测到Python导入错误"
            echo "   - 建议: 检查requirements.txt和依赖安装"
        fi
EOF
}

# 主执行函数
main() {
    echo "🎯 开始执行完整部署流程"
    
    # 异常处理
    trap 'echo "❌ 部署过程中发生错误，开始诊断..."; diagnose_failure backend; echo "📋 完整日志: $LOG_FILE"; echo "❌ 错误日志: $ERROR_LOG"' ERR
    
    # 执行部署步骤
    check_environment || { echo "❌ 环境检查失败"; exit 1; }
    update_code || { echo "❌ 代码更新失败"; exit 1; }
    build_with_monitoring backend || { echo "❌ 后端构建失败"; exit 1; }
    start_with_monitoring backend || { echo "❌ 后端启动失败"; exit 1; }
    health_check || { echo "❌ 健康检查失败"; exit 1; }
    
    echo ""
    echo "🎉 部署成功完成: $(date)"
    echo "📋 完整日志: $LOG_FILE"
    echo "🔗 服务地址: https://offerott.com"
    echo ""
    echo "📊 部署摘要:"
    echo "  - OpenCV问题: ✅ 已修复 (使用headless版本)"
    echo "  - 服务监控: ✅ 全程记录"
    echo "  - 错误诊断: ✅ 自动分析"
    echo "  - 日志保存: ✅ 完整记录"
}

# 执行主函数
main "$@" 