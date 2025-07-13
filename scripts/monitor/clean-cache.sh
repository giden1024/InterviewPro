#!/bin/bash

# ============================================
# InterviewPro 缓存清理脚本
# 清理本地和服务器的Docker、NPM、Git等缓存
# ============================================

set -e

# 配置信息
SERVER_IP="3.14.247.189"
KEY_FILE="aws-myy-rsa.pem"
REMOTE_USER="ubuntu"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 清理本地缓存
clean_local_cache() {
    log "🧹 清理本地缓存..."
    
    # 清理前端缓存
    if [ -d "frontend" ]; then
        log "清理前端缓存..."
        cd frontend
        
        # 清理构建产物
        rm -rf dist build .cache
        
        # 清理 node_modules 缓存
        if [ -d "node_modules" ]; then
            rm -rf node_modules/.cache
        fi
        
        # 清理 npm 缓存
        npm cache clean --force 2>/dev/null || true
        
        # 清理 vite 缓存
        rm -rf node_modules/.vite 2>/dev/null || true
        
        cd ..
        success "前端缓存已清理"
    fi
    
    # 清理后端缓存
    if [ -d "backend" ]; then
        log "清理后端缓存..."
        cd backend
        
        # 清理 Python 缓存
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        find . -name "*.pyo" -delete 2>/dev/null || true
        
        # 清理临时文件
        rm -rf .pytest_cache logs/* uploads/* 2>/dev/null || true
        
        cd ..
        success "后端缓存已清理"
    fi
    
    # 清理 Docker 缓存
    if command -v docker &> /dev/null; then
        log "清理Docker缓存..."
        
        # 清理未使用的镜像
        docker image prune -f 2>/dev/null || true
        
        # 清理未使用的容器
        docker container prune -f 2>/dev/null || true
        
        # 清理未使用的网络
        docker network prune -f 2>/dev/null || true
        
        # 清理未使用的卷
        docker volume prune -f 2>/dev/null || true
        
        # 清理构建缓存
        docker builder prune -f 2>/dev/null || true
        
        success "Docker缓存已清理"
    fi
    
    # 清理 Git 临时文件
    log "清理Git临时文件..."
    git gc --prune=now 2>/dev/null || true
    git remote prune origin 2>/dev/null || true
    success "Git临时文件已清理"
    
    # 清理本地部署包
    log "清理本地部署包..."
    rm -f *.tar.gz 2>/dev/null || true
    success "本地部署包已清理"
}

# 清理服务器缓存
clean_server_cache() {
    log "🌐 清理服务器缓存..."
    
    if [ ! -f "$KEY_FILE" ]; then
        error "SSH密钥文件 $KEY_FILE 不存在，跳过服务器清理"
        return 1
    fi
    
    # 测试SSH连接
    if ! ssh -i "$KEY_FILE" -o ConnectTimeout=10 "$REMOTE_USER@$SERVER_IP" "echo 'SSH连接成功'" 2>/dev/null; then
        error "SSH连接失败，跳过服务器清理"
        return 1
    fi
    
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" << 'EOF'
        echo "🐳 清理服务器Docker缓存..."
        
        # 停止所有容器（保持数据）
        docker stop $(docker ps -q) 2>/dev/null || true
        
        # 清理Docker缓存
        docker system prune -a -f 2>/dev/null || true
        docker builder prune -a -f 2>/dev/null || true
        docker volume prune -f 2>/dev/null || true
        
        echo "🗂️ 清理临时文件..."
        
        # 清理临时部署文件
        cd /home/ubuntu
        rm -f *.tar.gz 2>/dev/null || true
        rm -rf frontend-new-* backend-new-* 2>/dev/null || true
        
        # 清理系统临时文件
        rm -rf /tmp/*.backup /tmp/frontend-* /tmp/backend-* 2>/dev/null || true
        
        echo "💾 清理系统缓存..."
        
        # 清理APT缓存
        sudo apt-get clean 2>/dev/null || true
        sudo apt-get autoclean 2>/dev/null || true
        sudo apt-get autoremove -y 2>/dev/null || true
        
        # 清理日志文件（保留最近7天）
        sudo find /var/log -name "*.log" -mtime +7 -delete 2>/dev/null || true
        sudo journalctl --vacuum-time=7d 2>/dev/null || true
        
        echo "✅ 服务器缓存清理完成"
EOF
    
    success "服务器缓存已清理"
}

# 显示缓存清理前后的空间使用情况
show_disk_usage() {
    log "💾 磁盘空间使用情况："
    
    echo "本地磁盘使用："
    df -h . 2>/dev/null || true
    
    if [ -f "$KEY_FILE" ] && ssh -i "$KEY_FILE" -o ConnectTimeout=5 "$REMOTE_USER@$SERVER_IP" "echo 'test'" &>/dev/null; then
        echo ""
        echo "服务器磁盘使用："
        ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "df -h /home/ubuntu" 2>/dev/null || true
        
        echo ""
        echo "服务器Docker使用："
        ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "docker system df" 2>/dev/null || true
    fi
}

# 主函数
main() {
    log "🚀 开始缓存清理流程..."
    echo ""
    
    # 显示清理前的空间使用
    show_disk_usage
    echo ""
    
    # 询问清理范围
    echo "选择清理范围："
    echo "1) 仅清理本地缓存"
    echo "2) 仅清理服务器缓存"
    echo "3) 清理本地和服务器缓存（推荐）"
    echo "4) 退出"
    echo ""
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            clean_local_cache
            ;;
        2)
            clean_server_cache
            ;;
        3)
            clean_local_cache
            clean_server_cache
            ;;
        4)
            log "退出缓存清理"
            exit 0
            ;;
        *)
            error "无效选择"
            exit 1
            ;;
    esac
    
    echo ""
    success "🎉 缓存清理完成！"
    echo ""
    
    # 显示清理后的空间使用
    show_disk_usage
}

# 如果直接运行脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 