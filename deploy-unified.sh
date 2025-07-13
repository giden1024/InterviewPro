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

# 启动服务
start_services() {
    log "🚀 启动服务..."
    
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd $REMOTE_PATH
        
        echo '🐳 构建Docker镜像...'
        docker-compose -f docker-compose.prod.yml build --no-cache
        
        echo '🚀 启动服务...'
        docker-compose -f docker-compose.prod.yml up -d
        
        echo '⏳ 等待服务启动...'
        sleep 30
    "
    
    success "服务启动完成"
}

# 健康检查
health_check() {
    log "🏥 执行健康检查..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "健康检查 $attempt/$max_attempts..."
        
        # 检查容器状态
        local container_status=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
            cd $REMOTE_PATH && docker-compose -f docker-compose.prod.yml ps --format 'table' | grep -E '(frontend|backend|redis)' | grep -v 'Exit'
        " 2>/dev/null | wc -l)
        
        if [ "$container_status" -ge 3 ]; then
            # 检查API健康
            if curl -s -f "https://$SERVER_IP/api/v1/health" &>/dev/null; then
                success "健康检查通过！"
                return 0
            fi
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "健康检查失败"
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
    echo "访问地址："
    echo "  - 前端: https://$SERVER_IP"
    echo "  - API: https://$SERVER_IP/api/v1"
    echo "  - 健康检查: https://$SERVER_IP/api/v1/health"
    echo ""
    echo "部署ID: $DEPLOY_ID"
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