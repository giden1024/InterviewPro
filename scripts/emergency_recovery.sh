#!/bin/bash

# InterviewPro 紧急恢复脚本
# 使用方法: ./emergency_recovery.sh [option]

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "🚨 InterviewPro 紧急恢复系统"
echo "=================================="

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 检查系统状态
check_system_status() {
    echo -e "\n${CYAN}🔍 系统状态检查${NC}"
    echo "----------------------------------------"
    
    # 内存使用
    memory_usage=$(free | awk 'NR==2{printf "%.0f", ($3/$2)*100}')
    log_info "内存使用率: ${memory_usage}%"
    
    # 磁盘空间
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    log_info "磁盘使用率: ${disk_usage}%"
    
    # CPU负载
    load_avg=$(uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1 | xargs)
    log_info "系统负载: ${load_avg}"
    
    # Docker状态
    if docker ps &>/dev/null; then
        log_success "Docker服务正常"
    else
        log_error "Docker服务异常"
        return 1
    fi
    
    return 0
}

# 清理系统资源
cleanup_system() {
    echo -e "\n${CYAN}🧹 清理系统资源${NC}"
    echo "----------------------------------------"
    
    log_info "清理Docker缓存..."
    docker system prune -f
    
    log_info "清理未使用的Docker镜像..."
    docker image prune -f
    
    log_info "清理未使用的Docker容器..."
    docker container prune -f
    
    log_info "清理未使用的Docker网络..."
    docker network prune -f
    
    # 清理日志文件
    if [ -d "logs" ]; then
        log_info "清理应用日志..."
        find logs -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    fi
    
    log_success "系统资源清理完成"
}

# 快速重启所有服务
quick_restart() {
    echo -e "\n${CYAN}🔄 快速重启所有服务${NC}"
    echo "----------------------------------------"
    
    log_info "停止所有服务..."
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    cleanup_system
    
    log_info "启动基础服务..."
    docker-compose -f docker-compose.prod.yml up -d mysql redis
    sleep 30
    
    log_info "启动应用服务..."
    docker-compose -f docker-compose.prod.yml up -d backend
    sleep 20
    
    log_info "启动Web服务..."
    docker-compose -f docker-compose.prod.yml up -d nginx
    sleep 10
    
    log_success "服务重启完成"
}

# 重建Backend服务
rebuild_backend() {
    echo -e "\n${CYAN}🔨 重建Backend服务${NC}"
    echo "----------------------------------------"
    
    log_info "停止Backend服务..."
    docker-compose -f docker-compose.prod.yml stop backend
    
    log_info "删除Backend镜像..."
    docker-compose -f docker-compose.prod.yml rm -f backend
    docker rmi $(docker images | grep backend | awk '{print $3}') 2>/dev/null || true
    
    log_info "重新构建Backend镜像..."
    docker-compose -f docker-compose.prod.yml build --no-cache backend
    
    log_info "启动Backend服务..."
    docker-compose -f docker-compose.prod.yml up -d backend
    
    log_success "Backend重建完成"
}

# 恢复到备份配置
restore_backup() {
    echo -e "\n${CYAN}📁 恢复备份配置${NC}"
    echo "----------------------------------------"
    
    if [ ! -d "backups" ]; then
        log_error "没有找到备份目录"
        return 1
    fi
    
    # 列出可用备份
    echo "可用备份:"
    ls -la backups/ | grep "^d" | awk '{print $9}' | grep -v "^\.$\|^\.\.$"
    
    echo ""
    read -p "请输入备份目录名称 (格式: YYYYMMDD_HHMMSS): " backup_dir
    
    if [ ! -d "backups/$backup_dir" ]; then
        log_error "备份目录不存在: $backup_dir"
        return 1
    fi
    
    log_info "停止所有服务..."
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    log_info "恢复配置文件..."
    
    if [ -f "backups/$backup_dir/docker-compose.prod.yml" ]; then
        cp "backups/$backup_dir/docker-compose.prod.yml" .
        log_success "恢复 docker-compose.prod.yml"
    fi
    
    if [ -f "backups/$backup_dir/requirements.txt" ]; then
        cp "backups/$backup_dir/requirements.txt" backend/
        log_success "恢复 requirements.txt"
    fi
    
    if [ -f "backups/$backup_dir/Dockerfile.prod" ]; then
        cp "backups/$backup_dir/Dockerfile.prod" backend/
        log_success "恢复 Dockerfile.prod"
    fi
    
    log_info "重新启动服务..."
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "备份恢复完成"
}

# 创建Swap分区
create_swap() {
    echo -e "\n${CYAN}💾 创建Swap分区${NC}"
    echo "----------------------------------------"
    
    # 检查是否已有Swap
    if swapon --show | grep -q "swapfile"; then
        log_warn "Swap分区已存在"
        return 0
    fi
    
    log_info "创建2GB Swap文件..."
    sudo fallocate -l 2G /swapfile
    
    log_info "设置权限..."
    sudo chmod 600 /swapfile
    
    log_info "设置Swap格式..."
    sudo mkswap /swapfile
    
    log_info "启用Swap..."
    sudo swapon /swapfile
    
    log_info "添加到开机自启..."
    if ! grep -q "/swapfile" /etc/fstab; then
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi
    
    log_success "Swap分区创建完成"
}

# 修复权限问题
fix_permissions() {
    echo -e "\n${CYAN}🔒 修复权限问题${NC}"
    echo "----------------------------------------"
    
    log_info "修复项目文件权限..."
    
    # 修复目录权限
    find . -type d -exec chmod 755 {} \; 2>/dev/null || true
    
    # 修复文件权限
    find . -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # 修复脚本权限
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x *.sh 2>/dev/null || true
    
    # 修复Docker相关文件
    chmod 644 docker-compose*.yml 2>/dev/null || true
    chmod 644 backend/Dockerfile* 2>/dev/null || true
    
    log_success "权限修复完成"
}

# 完整恢复流程
full_recovery() {
    echo -e "\n${CYAN}🏥 完整恢复流程${NC}"
    echo "----------------------------------------"
    
    log_warn "这将执行完整的恢复流程，包括："
    echo "1. 停止所有服务"
    echo "2. 清理系统资源"
    echo "3. 修复权限问题"
    echo "4. 重建所有服务"
    echo "5. 启动服务"
    echo ""
    
    read -p "确认执行完整恢复? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "恢复已取消"
        return 0
    fi
    
    # 1. 停止所有服务
    log_info "1/5 停止所有服务..."
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # 2. 清理系统资源
    log_info "2/5 清理系统资源..."
    cleanup_system
    
    # 3. 修复权限
    log_info "3/5 修复权限问题..."
    fix_permissions
    
    # 4. 重建服务
    log_info "4/5 重建所有服务..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # 5. 启动服务
    log_info "5/5 启动服务..."
    docker-compose -f docker-compose.prod.yml up -d mysql redis
    sleep 30
    docker-compose -f docker-compose.prod.yml up -d backend
    sleep 20
    docker-compose -f docker-compose.prod.yml up -d nginx
    
    log_success "完整恢复流程完成"
}

# 显示服务状态
show_status() {
    echo -e "\n${CYAN}📊 当前服务状态${NC}"
    echo "----------------------------------------"
    
    if docker-compose -f docker-compose.prod.yml ps &>/dev/null; then
        docker-compose -f docker-compose.prod.yml ps
        
        echo -e "\n容器资源使用:"
        docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'
        
        echo -e "\n应用健康检查:"
        if curl -f -s http://localhost:8080/ &>/dev/null; then
            log_success "Backend API正常"
        else
            log_error "Backend API异常"
        fi
        
        if curl -f -s http://localhost/ &>/dev/null; then
            log_success "前端页面正常"
        else
            log_error "前端页面异常"
        fi
    else
        log_error "无法访问Docker服务"
    fi
}

# 显示菜单
show_menu() {
    echo ""
    echo "请选择恢复选项:"
    echo "1) 检查系统状态"
    echo "2) 快速重启服务"
    echo "3) 重建Backend服务"
    echo "4) 清理系统资源"
    echo "5) 恢复备份配置"
    echo "6) 创建Swap分区"
    echo "7) 修复权限问题"
    echo "8) 完整恢复流程"
    echo "9) 显示服务状态"
    echo "0) 退出"
    echo ""
}

# 主函数
main() {
    # 检查Docker权限
    if ! docker ps &>/dev/null; then
        log_error "无法访问Docker，请检查权限或确保Docker服务正在运行"
        exit 1
    fi
    
    # 如果有参数，直接执行对应功能
    case "$1" in
        "status")
            check_system_status
            show_status
            exit 0
            ;;
        "restart")
            quick_restart
            exit 0
            ;;
        "rebuild")
            rebuild_backend
            exit 0
            ;;
        "cleanup")
            cleanup_system
            exit 0
            ;;
        "full")
            full_recovery
            exit 0
            ;;
    esac
    
    # 交互式菜单
    while true; do
        show_menu
        read -p "请选择 [0-9]: " choice
        
        case $choice in
            1)
                check_system_status
                ;;
            2)
                quick_restart
                ;;
            3)
                rebuild_backend
                ;;
            4)
                cleanup_system
                ;;
            5)
                restore_backup
                ;;
            6)
                create_swap
                ;;
            7)
                fix_permissions
                ;;
            8)
                full_recovery
                ;;
            9)
                show_status
                ;;
            0)
                log_info "退出恢复系统"
                exit 0
                ;;
            *)
                log_error "无效选择，请重新输入"
                ;;
        esac
        
        echo ""
        read -p "按回车键继续..."
    done
}

# 执行主函数
main "$@" 