#!/bin/bash

# ============================================
# InterviewPro 统一部署脚本
# 包含：预检查、缓存清理、原子化部署、回滚机制
# ============================================

set -e

# 配置信息
SERVER_IP="3.14.247.189"
KEY_FILE="aws-myy-rsa.pem"
REMOTE_USER="ubuntu"
PROJECT_NAME="InterviewPro"
REMOTE_PATH="/home/ubuntu/$PROJECT_NAME"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 生成唯一的部署ID
DEPLOY_ID="deploy_$(date +%Y%m%d_%H%M%S)"

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# 检查必要文件和环境
check_prerequisites() {
    log "🔍 检查部署前提条件..."
    
    # 检查SSH密钥
    if [ ! -f "$KEY_FILE" ]; then
        error "SSH密钥文件 $KEY_FILE 不存在"
        exit 1
    fi
    
    # 检查项目目录
    if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
        error "请在项目根目录执行此脚本"
        exit 1
    fi
    
    # 检查必要工具
    for tool in git docker npm ssh; do
        if ! command -v $tool &> /dev/null; then
            error "$tool 未安装"
            exit 1
        fi
    done
    
    success "前提条件检查通过"
}

# 检查Git状态
check_git_status() {
    log "📋 检查Git状态..."
    
    # 检查是否有未提交的更改
    if ! git diff --quiet; then
        warning "存在未提交的本地更改："
        git diff --stat
        read -p "是否继续部署？ (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "部署已取消"
            exit 1
        fi
    fi
    
    # 检查是否与远程同步
    git fetch origin main
    if [ $(git rev-list HEAD...origin/main --count) != 0 ]; then
        warning "本地分支与远程不同步："
        git log --oneline HEAD...origin/main
        read -p "是否拉取最新代码？ (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git pull origin main
        fi
    fi
    
    success "Git状态检查完成"
}

# 测试SSH连接
test_ssh_connection() {
    log "🔗 测试SSH连接..."
    
    if ! ssh -i "$KEY_FILE" -o ConnectTimeout=10 "$REMOTE_USER@$SERVER_IP" "echo 'SSH连接成功'" 2>/dev/null; then
        error "SSH连接失败，请检查服务器状态和网络连接"
        exit 1
    fi
    
    success "SSH连接正常"
}

# 清理本地缓存
clean_local_cache() {
    log "🧹 清理本地缓存..."
    
    # 清理前端
    cd frontend
    rm -rf dist node_modules/.cache
    success "前端缓存已清理"
    cd ..
    
    # 清理Docker
    if docker info &>/dev/null; then
        docker system prune -f &>/dev/null || true
        success "Docker缓存已清理"
    fi
}

# 构建前端应用
build_frontend() {
    log "📦 构建前端应用..."
    
    cd frontend
    
    # 安装依赖
    log "安装前端依赖..."
    npm ci --silent
    
    # 构建生产版本
    log "构建生产版本..."
    if ! npm run build; then
        error "前端构建失败"
        exit 1
    fi
    
    if [ ! -d "dist" ]; then
        error "构建失败，dist目录不存在"
        exit 1
    fi
    
    # 创建部署包
    cd dist
    tar --no-xattrs -czf "../../frontend-${DEPLOY_ID}.tar.gz" .
    cd ../..
    
    success "前端构建完成，部署包：frontend-${DEPLOY_ID}.tar.gz"
}

# 准备后端部署包
prepare_backend() {
    log "📦 准备后端部署包..."
    
    # 创建后端部署包
    tar --no-xattrs -czf "backend-${DEPLOY_ID}.tar.gz" \
        --exclude='venv' \
        --exclude='instance' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='logs' \
        --exclude='uploads' \
        backend/
    
    success "后端部署包已创建：backend-${DEPLOY_ID}.tar.gz"
}

# 创建服务器备份
create_server_backup() {
    log "💾 创建服务器备份..."
    
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        if [ -d '$REMOTE_PATH' ]; then
            # 停止服务
            cd $REMOTE_PATH
            docker-compose -f docker-compose.prod.yml down &>/dev/null || true
            
            # 创建备份
            cd /home/ubuntu
            if [ -d '${PROJECT_NAME}-backup-${DEPLOY_ID}' ]; then
                rm -rf '${PROJECT_NAME}-backup-${DEPLOY_ID}'
            fi
            cp -r '$PROJECT_NAME' '${PROJECT_NAME}-backup-${DEPLOY_ID}'
            echo '✅ 服务器备份已创建：${PROJECT_NAME}-backup-${DEPLOY_ID}'
        else
            echo '⚠️  项目目录不存在，跳过备份'
        fi
    "
    
    success "服务器备份完成"
}

# 上传文件到服务器
upload_files() {
    log "📤 上传文件到服务器..."
    
    # 上传前端
    log "上传前端文件..."
    scp -i "$KEY_FILE" "frontend-${DEPLOY_ID}.tar.gz" "$REMOTE_USER@$SERVER_IP:/home/ubuntu/"
    
    # 上传后端
    log "上传后端文件..."
    scp -i "$KEY_FILE" "backend-${DEPLOY_ID}.tar.gz" "$REMOTE_USER@$SERVER_IP:/home/ubuntu/"
    
    success "文件上传完成"
}

# 部署到服务器
deploy_to_server() {
    log "🚀 部署到服务器..."
    
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" << EOF
        set -e
        
        echo "📁 准备部署目录..."
        mkdir -p $REMOTE_PATH
        cd /home/ubuntu
        
        echo "🔄 清理服务器Docker缓存..."
        docker system prune -a -f &>/dev/null || true
        
        echo "📦 解压前端文件..."
        mkdir -p frontend-new-${DEPLOY_ID}
        cd frontend-new-${DEPLOY_ID}
        tar -xzf ../frontend-${DEPLOY_ID}.tar.gz
        
        echo "📦 解压后端文件..."
        cd /home/ubuntu
        mkdir -p backend-new-${DEPLOY_ID}
        cd backend-new-${DEPLOY_ID}
        tar -xzf ../backend-${DEPLOY_ID}.tar.gz
        
        echo "🔄 部署新版本..."
        # 备份重要配置文件
        if [ -f "$REMOTE_PATH/docker-compose.prod.yml" ]; then
            cp "$REMOTE_PATH/docker-compose.prod.yml" /tmp/docker-compose.prod.yml.backup
        fi
        if [ -f "$REMOTE_PATH/.env.production" ]; then
            cp "$REMOTE_PATH/.env.production" /tmp/.env.production.backup
        fi
        
        # 清理并重新创建项目目录
        rm -rf $REMOTE_PATH/*
        
        # 复制新的后端代码
        cp -r backend-new-${DEPLOY_ID}/backend/* $REMOTE_PATH/
        
        # 创建前端目录并复制文件
        mkdir -p $REMOTE_PATH/frontend/dist
        cp -r frontend-new-${DEPLOY_ID}/* $REMOTE_PATH/frontend/dist/
        
        # 恢复配置文件
        if [ -f "/tmp/docker-compose.prod.yml.backup" ]; then
            cp /tmp/docker-compose.prod.yml.backup $REMOTE_PATH/docker-compose.prod.yml
        fi
        if [ -f "/tmp/.env.production.backup" ]; then
            cp /tmp/.env.production.backup $REMOTE_PATH/.env.production
        fi
        
        echo "✅ 新版本部署完成"
EOF
    
    success "服务器部署完成"
}

# 启动服务（带资源监控和CPU保护）
start_services() {
    log "🚀 启动服务..."
    
    # 检查系统资源状态
    log "📊 检查部署前系统资源..."
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        echo '=== 部署前系统状态 ==='
        echo 'CPU使用率:'
        top -bn1 | grep 'Cpu(s)' | head -1
        echo '内存使用:'
        free -h | grep Mem
        echo '负载平均值:'
        uptime
        echo '========================'
    "
    
    # 停止现有服务，防止资源冲突
    log "🛑 安全停止现有服务..."
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd $REMOTE_PATH
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
        sleep 5
        
        # 清理系统缓存
        echo '清理系统缓存...'
        sync
        echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true
    "
    
    # 构建镜像
    log "🐳 构建Docker镜像..."
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd $REMOTE_PATH
        docker-compose -f docker-compose.prod.yml build --no-cache
    "
    
    # 分阶段启动服务
    log "🗄️ 分阶段启动 - 数据库层..."
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd $REMOTE_PATH
        echo '启动数据库服务...'
        docker-compose -f docker-compose.prod.yml up -d mysql redis 2>/dev/null || \
        docker-compose -f docker-compose.prod.yml up -d mysql redis
        sleep 15
        
        echo '检查数据库状态...'
        docker-compose -f docker-compose.prod.yml ps
    "
    
    log "🔧 启动应用层..."
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd $REMOTE_PATH
        echo '启动后端服务...'
        docker-compose -f docker-compose.prod.yml up -d backend
        sleep 20
        
        echo '检查后端状态和CPU使用率...'
        docker-compose -f docker-compose.prod.yml ps | grep backend
        top -bn1 | grep 'Cpu(s)' | head -1
    "
    
    # CPU使用率安全检查
    log "⚠️ 执行CPU使用率安全检查..."
    local cpu_usage=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1 | tr -d ' ,'
    " 2>/dev/null || echo "0")
    
    log "当前CPU使用率: ${cpu_usage}%"
    
    # 检查CPU使用率是否过高
    if [ "${cpu_usage}" != "0" ] && [ "${cpu_usage%.*}" -gt 80 ] 2>/dev/null; then
        error "⚠️ CPU使用率过高 (${cpu_usage}%)，停止部署并回滚"
        ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
            cd $REMOTE_PATH
            echo '紧急停止高负载服务...'
            docker-compose -f docker-compose.prod.yml down
            echo '清理资源...'
            docker system prune -f
        "
        return 1
    fi
    
    log "✅ CPU使用率正常，继续启动前端服务..."
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd $REMOTE_PATH
        echo '启动前端服务...'
        docker-compose -f docker-compose.prod.yml up -d frontend nginx 2>/dev/null || \
        docker-compose -f docker-compose.prod.yml up -d nginx
        
        echo '⏳ 等待所有服务稳定...'
        sleep 20
        
        echo '📊 最终服务状态检查...'
        docker-compose -f docker-compose.prod.yml ps
        
        echo '📈 系统资源最终状态:'
        echo 'CPU使用率:'
        top -bn1 | grep 'Cpu(s)' | head -1
        echo '内存使用:'
        free -h | grep Mem
        
        echo '🐳 Docker容器资源使用:'
        timeout 10 docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}' 2>/dev/null || echo '容器资源信息获取超时'
        
        echo '✅ 新版本部署完成'
    "
    
    success "服务启动完成"
}

# 健康检查
health_check() {
    log "🏥 执行健康检查和外部访问验证..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "健康检查 $attempt/$max_attempts..."
        
        # 检查容器状态
        local container_status=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
            cd $REMOTE_PATH && docker-compose -f docker-compose.prod.yml ps --format 'table' | grep -E '(frontend|backend|redis)' | grep -v 'Exit'
        " 2>/dev/null | wc -l)
        
        if [ "$container_status" -ge 3 ]; then
            # 内部服务检查
            log "检查内部服务状态..."
            local internal_check=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
                # 检查本地服务
                curl -s http://localhost/ -o /dev/null -w '%{http_code}' &
                curl -s http://localhost:5001/api/health -o /dev/null -w '%{http_code}' &
                wait
                echo 'done'
            " 2>/dev/null)
            
            # 外部访问检查
            log "检查外部访问状态..."
            
            # 检查主网站 (HTTPS)
            local https_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://offerott.com/" || echo "000")
            log "HTTPS访问状态码: $https_status"
            
            # 检查API端点
            local api_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://offerott.com/api/health" || echo "000")
            log "API访问状态码: $api_status"
            
            # 检查HTTP重定向
            local http_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "http://offerott.com/" || echo "000")
            log "HTTP重定向状态码: $http_status"
            
            # 成功条件：主网站200，API可访问
            if [ "$https_status" = "200" ] && [ "$api_status" -eq "$api_status" ] 2>/dev/null; then
                success "✅ 外部访问检查通过！"
                
                # 额外的内容验证
                log "验证网站内容..."
                local content_check=$(curl -s "https://offerott.com/" | head -100 | grep -i "interviewpro\|html\|<!DOCTYPE" | wc -l)
                if [ "$content_check" -gt 0 ]; then
                    success "✅ 网站内容验证通过！"
                    return 0
                else
                    warning "⚠️ 网站内容可能有问题，但连接正常"
                    return 0
                fi
            elif [ "$https_status" = "502" ]; then
                warning "⚠️ 检测到502错误，尝试自动修复..."
                
                # 尝试自动修复502错误
                ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
                    echo '🔧 自动修复502错误...'
                    cd $REMOTE_PATH
                    sudo systemctl restart nginx
                    docker-compose restart
                    sleep 10
                "
                
                # 再次检查
                local retry_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://offerott.com/" || echo "000")
                if [ "$retry_status" = "200" ]; then
                    success "✅ 502错误修复成功！"
                    return 0
                else
                    warning "⚠️ 502错误未能自动修复，状态码: $retry_status"
                fi
            else
                warning "⚠️ 外部访问检查: HTTPS=$https_status, API=$api_status, HTTP=$http_status"
            fi
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "❌ 健康检查和外部访问验证失败"
            log "最终状态: HTTPS=$https_status, API=$api_status"
            return 1
        fi
        
        sleep 15
        ((attempt++))
    done
}

# 回滚函数
rollback() {
    error "部署失败，开始回滚..."
    
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        if [ -d '/home/ubuntu/${PROJECT_NAME}-backup-${DEPLOY_ID}' ]; then
            echo '🔄 回滚到备份版本...'
            cd /home/ubuntu
            docker-compose -f $REMOTE_PATH/docker-compose.prod.yml down &>/dev/null || true
            rm -rf '$REMOTE_PATH'
            mv '${PROJECT_NAME}-backup-${DEPLOY_ID}' '$PROJECT_NAME'
            cd $REMOTE_PATH
            docker-compose -f docker-compose.prod.yml up -d &>/dev/null || true
            echo '✅ 回滚完成'
        else
            echo '❌ 备份不存在，无法回滚'
        fi
    "
    
    warning "已回滚到之前的版本"
}

# 清理临时文件
cleanup() {
    log "🧹 清理临时文件..."
    
    # 清理本地临时文件
    rm -f "frontend-${DEPLOY_ID}.tar.gz" "backend-${DEPLOY_ID}.tar.gz"
    
    # 清理服务器临时文件
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd /home/ubuntu
        rm -f frontend-${DEPLOY_ID}.tar.gz backend-${DEPLOY_ID}.tar.gz
        rm -rf frontend-new-${DEPLOY_ID} backend-new-${DEPLOY_ID}
    " &>/dev/null || true
    
    success "临时文件清理完成"
}

# 显示部署结果
show_deploy_result() {
    log "📊 部署结果："
    
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd $REMOTE_PATH
        echo '容器状态：'
        docker-compose -f docker-compose.prod.yml ps
        echo ''
        echo '服务检查：'
        curl -s https://$SERVER_IP/api/v1/health | jq . 2>/dev/null || curl -s https://$SERVER_IP/api/v1/health
    "
    
    success "🎉 部署完成！"
    echo ""
    
    # 执行最终外部访问验证
    log "🌐 执行最终外部访问验证..."
    
    # 检查主要访问地址
    local final_https_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "https://offerott.com/" || echo "000")
    local final_api_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "https://offerott.com/api/health" || echo "000")
    local final_http_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "http://offerott.com/" || echo "000")
    
    echo "📊 外部访问验证结果："
    if [ "$final_https_status" = "200" ]; then
        success "  ✅ HTTPS主站: https://offerott.com/ (状态码: $final_https_status)"
    else
        error "  ❌ HTTPS主站: https://offerott.com/ (状态码: $final_https_status)"
    fi
    
    if [ "$final_api_status" = "200" ] || [ "$final_api_status" = "404" ]; then
        success "  ✅ API端点: https://offerott.com/api/health (状态码: $final_api_status)"
    else
        warning "  ⚠️ API端点: https://offerott.com/api/health (状态码: $final_api_status)"
    fi
    
    if [ "$final_http_status" = "301" ] || [ "$final_http_status" = "302" ]; then
        success "  ✅ HTTP重定向: http://offerott.com/ (状态码: $final_http_status - 正常重定向到HTTPS)"
    elif [ "$final_http_status" = "200" ]; then
        warning "  ⚠️ HTTP访问: http://offerott.com/ (状态码: $final_http_status - 应该重定向到HTTPS)"
    else
        error "  ❌ HTTP访问: http://offerott.com/ (状态码: $final_http_status)"
    fi
    
    # 性能测试
    log "🚀 执行性能测试..."
    local response_time=$(curl -s -o /dev/null -w "%{time_total}" --connect-timeout 10 "https://offerott.com/" || echo "timeout")
    if [ "$response_time" != "timeout" ]; then
        local response_ms=$(echo "$response_time * 1000" | bc 2>/dev/null || echo "$response_time")
        success "  ✅ 响应时间: ${response_ms}ms"
    else
        warning "  ⚠️ 响应时间测试超时"
    fi
    
    echo ""
    echo "🌐 访问地址："
    echo "  - 主站: https://offerott.com/"
    echo "  - 备用: https://$SERVER_IP"
    echo "  - API: https://offerott.com/api/"
    echo "  - 健康检查: https://offerott.com/api/health"
    echo ""
    echo "🔧 管理工具："
    echo "  - 部署ID: $DEPLOY_ID"
    echo "  - 回滚: ./rollback.sh --rollback $DEPLOY_ID"
    echo "  - 502修复: ./fix-502-error.sh"
    echo ""
    
    # 最终状态总结
    if [ "$final_https_status" = "200" ]; then
        success "🎉 网站部署成功并通过外部访问验证！"
    else
        warning "⚠️ 网站部署完成，但外部访问可能存在问题，请运行: ./fix-502-error.sh"
    fi
}

# 主函数
main() {
    log "🚀 开始 InterviewPro 统一部署流程..."
    log "部署ID: $DEPLOY_ID"
    echo ""
    
    # 设置错误处理
    trap 'error "部署过程中发生错误"; rollback; cleanup; exit 1' ERR
    
    # 执行部署步骤
    check_prerequisites
    check_git_status
    test_ssh_connection
    clean_local_cache
    build_frontend
    prepare_backend
    create_server_backup
    upload_files
    deploy_to_server
    start_services
    
    # 健康检查
    if ! health_check; then
        rollback
        cleanup
        exit 1
    fi
    
    # 显示结果
    show_deploy_result
    cleanup
    
    success "🎉 部署成功完成！"
}

# 执行主函数
main "$@" 