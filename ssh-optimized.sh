#!/bin/bash

# 优化的SSH连接脚本
# 解决连接超时和banner exchange问题

set -e

# 配置参数
SERVER_IP="3.14.247.189"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"
SSH_USER="ubuntu"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 优化的SSH连接函数
ssh_connect() {
    local command="$1"
    local max_attempts=5
    local attempt=1
    
    log "准备执行SSH命令: $command"
    
    while [ $attempt -le $max_attempts ]; do
        log "SSH连接尝试 $attempt/$max_attempts..."
        
        if timeout 45 ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" \
            -o ConnectTimeout=20 \
            -o ServerAliveInterval=5 \
            -o ServerAliveCountMax=3 \
            -o TCPKeepAlive=yes \
            -o Compression=yes \
            -o StrictHostKeyChecking=no \
            -o BatchMode=yes \
            "$command" 2>/dev/null; then
            success "SSH命令执行成功"
            return 0
        fi
        
        warn "连接尝试 $attempt 失败，等待5秒后重试..."
        sleep 5
        ((attempt++))
    done
    
    error "所有SSH连接尝试都失败了"
    return 1
}

# 快速状态检查
quick_status_check() {
    log "🔍 执行快速状态检查..."
    
    # 检查基本连接
    if ssh_connect "echo 'SSH连接正常'"; then
        success "SSH连接测试通过"
    else
        error "SSH连接测试失败"
        return 1
    fi
    
    # 检查Docker服务
    log "检查Docker服务状态..."
    if ssh_connect "docker ps --format 'table {{.Names}}\t{{.Status}}' | head -5"; then
        success "Docker服务检查完成"
    else
        warn "Docker服务检查失败"
    fi
    
    # 检查Nginx服务
    log "检查Nginx服务状态..."
    if ssh_connect "sudo systemctl is-active nginx"; then
        success "Nginx服务运行正常"
    else
        warn "Nginx服务可能有问题"
    fi
}

# 修复502错误的优化版本
fix_502_optimized() {
    log "🔧 开始优化的502错误修复流程..."
    
    # 步骤1: 重启Nginx
    log "步骤1: 重启系统Nginx服务..."
    if ssh_connect "sudo systemctl restart nginx && sudo systemctl enable nginx"; then
        success "Nginx重启成功"
    else
        error "Nginx重启失败"
        return 1
    fi
    
    # 等待5秒
    sleep 5
    
    # 步骤2: 重启Docker服务
    log "步骤2: 重启Docker容器..."
    if ssh_connect "cd /home/ubuntu/InterviewPro && docker-compose down"; then
        success "Docker服务停止成功"
    else
        warn "Docker服务停止可能有问题"
    fi
    
    # 等待5秒
    sleep 5
    
    if ssh_connect "cd /home/ubuntu/InterviewPro && docker-compose up -d"; then
        success "Docker服务启动成功"
    else
        error "Docker服务启动失败"
        return 1
    fi
    
    # 步骤3: 等待服务稳定
    log "步骤3: 等待服务稳定..."
    sleep 20
    
    # 步骤4: 验证服务状态
    log "步骤4: 验证服务状态..."
    ssh_connect "docker ps --format 'table {{.Names}}\t{{.Status}}'"
    ssh_connect "sudo systemctl is-active nginx && echo 'Nginx: 运行正常' || echo 'Nginx: 异常'"
    ssh_connect "curl -s http://localhost/ > /dev/null && echo '本地前端: 正常' || echo '本地前端: 异常'"
    
    success "修复流程完成"
}

# 外部访问验证
external_access_check() {
    log "🌐 执行外部访问验证..."
    
    # 检查HTTPS
    local https_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "https://offerott.com/" || echo "000")
    log "HTTPS状态: $https_status"
    
    # 检查HTTP
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "http://offerott.com/" || echo "000")
    log "HTTP状态: $http_status"
    
    # 结果分析
    if [ "$https_status" = "200" ]; then
        success "✅ 网站访问正常: https://offerott.com/"
        return 0
    elif [ "$https_status" = "502" ]; then
        error "❌ 502错误仍然存在"
        return 1
    else
        warn "⚠️ 网站状态异常: $https_status"
        return 2
    fi
}

# 主函数
main() {
    echo "🚀 InterviewPro 优化SSH连接和502修复工具"
    echo "============================================"
    
    case "${1:-status}" in
        "status")
            quick_status_check
            external_access_check
            ;;
        "fix")
            fix_502_optimized
            external_access_check
            ;;
        "connect")
            shift
            ssh_connect "$*"
            ;;
        *)
            echo "用法: $0 [status|fix|connect <command>]"
            echo "  status  - 检查服务器和网站状态"
            echo "  fix     - 修复502错误"
            echo "  connect - 执行自定义SSH命令"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 