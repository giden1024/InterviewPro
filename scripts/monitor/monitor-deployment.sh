#!/bin/bash

# 新服务器部署监控脚本

SERVER_IP="18.219.240.36"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"
SSH_USER="ec2-user"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 快速SSH连接
quick_ssh() {
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" \
        -o ConnectTimeout=10 \
        -o StrictHostKeyChecking=no \
        -o BatchMode=yes \
        "$1" 2>/dev/null
}

# 检查服务器状态
check_server_status() {
    log "🔍 检查服务器状态..."
    
    if ! quick_ssh "echo 'SSH连接正常'"; then
        error "无法连接到服务器"
        return 1
    fi
    
    # 系统资源
    local cpu_usage=$(quick_ssh "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1 | tr -d ' ,'")
    local mem_usage=$(quick_ssh "free | grep Mem | awk '{printf \"%.1f\", \$3/\$2 * 100.0}'")
    local load_avg=$(quick_ssh "uptime | awk '{print \$(NF-2)}' | tr -d ','")
    
    echo "📊 系统资源:"
    echo "  CPU使用率: ${cpu_usage}%"
    echo "  内存使用率: ${mem_usage}%"
    echo "  负载平均值: ${load_avg}"
    
    # 检查Docker
    if quick_ssh "docker --version" > /dev/null 2>&1; then
        success "✅ Docker已安装"
        
        # 检查容器状态
        local containers=$(quick_ssh "docker ps --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null" || echo "")
        if [ -n "$containers" ]; then
            echo "🐳 Docker容器状态:"
            echo "$containers"
        else
            warning "⚠️ 没有运行中的容器"
        fi
    else
        warning "⚠️ Docker未安装或未启动"
    fi
    
    # 检查项目目录
    if quick_ssh "[ -d /home/ec2-user/InterviewPro ]"; then
        success "✅ 项目目录存在"
        
        # 检查Docker Compose文件
        if quick_ssh "[ -f /home/ec2-user/InterviewPro/docker-compose.yml ]"; then
            success "✅ Docker Compose配置存在"
        else
            warning "⚠️ Docker Compose配置缺失"
        fi
    else
        warning "⚠️ 项目目录不存在"
    fi
    
    echo ""
}

# 检查网站访问
check_website() {
    log "🌐 检查网站访问..."
    
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "http://$SERVER_IP/" 2>/dev/null || echo "000")
    
    echo "网站状态码: $http_status"
    
    if [ "$http_status" = "200" ]; then
        success "✅ 网站可以正常访问: http://$SERVER_IP/"
    elif [ "$http_status" = "502" ]; then
        warning "⚠️ 网站显示502错误，可能还在启动中"
    elif [ "$http_status" = "000" ]; then
        warning "⚠️ 网站无法连接，可能还未部署完成"
    else
        warning "⚠️ 网站状态码: $http_status"
    fi
    
    echo ""
}

# 检查部署进程
check_deployment_process() {
    log "🔄 检查部署进程..."
    
    # 检查是否有部署相关进程
    local deploy_process=$(quick_ssh "ps aux | grep -E '(docker|dnf|yum|curl)' | grep -v grep | wc -l")
    
    if [ "$deploy_process" -gt 0 ]; then
        warning "⚠️ 检测到 $deploy_process 个部署相关进程在运行"
        echo "部署可能仍在进行中..."
    else
        success "✅ 没有检测到活跃的部署进程"
    fi
    
    echo ""
}

# 显示部署建议
show_recommendations() {
    echo "💡 建议和下一步:"
    echo ""
    
    # 检查网站状态决定建议
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://$SERVER_IP/" 2>/dev/null || echo "000")
    
    if [ "$http_status" = "200" ]; then
        success "🎉 部署完成！网站正常运行"
        echo "  - 访问网站: http://$SERVER_IP/"
        echo "  - 管理命令: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'cd /home/ec2-user/InterviewPro && docker-compose ps'"
    elif [ "$http_status" = "502" ] || [ "$http_status" = "000" ]; then
        echo "  - 等待部署完成，或检查部署状态"
        echo "  - 如果长时间无响应，可能需要手动检查"
        echo "  - 连接服务器: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP"
    fi
    
    echo ""
    echo "🔧 常用管理命令:"
    echo "  - 查看容器状态: docker-compose ps"
    echo "  - 查看日志: docker-compose logs"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 停止服务: docker-compose down"
    echo ""
}

# 主函数
main() {
    echo "📊 InterviewPro 新服务器部署监控"
    echo "================================="
    echo "服务器: $SERVER_IP"
    echo "监控时间: $(date)"
    echo ""
    
    check_server_status
    check_deployment_process
    check_website
    show_recommendations
}

# 持续监控模式
continuous_monitor() {
    while true; do
        clear
        main
        echo "按 Ctrl+C 停止监控，或等待30秒自动刷新..."
        sleep 30
    done
}

# 检查参数
case "${1:-single}" in
    "continuous"|"watch")
        continuous_monitor
        ;;
    "single"|*)
        main
        ;;
esac 