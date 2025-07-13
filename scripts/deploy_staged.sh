#!/bin/bash

# InterviewPro 分阶段部署脚本
# 使用方法: ./deploy_staged.sh

echo "🚀 InterviewPro 分阶段部署开始..."
echo "=================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 等待函数
wait_for_service() {
    local service=$1
    local timeout=$2
    local count=0
    
    log_info "等待 $service 服务启动..."
    
    while [ $count -lt $timeout ]; do
        if docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up"; then
            log_success "$service 服务已启动"
            return 0
        fi
        sleep 5
        count=$((count + 5))
        echo -n "."
    done
    
    log_error "$service 服务启动超时"
    return 1
}

# 检查服务健康状态
check_service_health() {
    local service=$1
    log_info "检查 $service 服务健康状态..."
    
    docker-compose -f docker-compose.prod.yml logs $service --tail=10
    
    if docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up"; then
        log_success "$service 服务运行正常"
        return 0
    else
        log_error "$service 服务运行异常"
        return 1
    fi
}

# 备份现有配置
backup_configs() {
    log_info "备份现有配置..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    mkdir -p backups/$timestamp
    
    if [ -f "docker-compose.prod.yml" ]; then
        cp docker-compose.prod.yml backups/$timestamp/
        log_success "备份 docker-compose.prod.yml"
    fi
    
    if [ -f "backend/requirements.txt" ]; then
        cp backend/requirements.txt backups/$timestamp/
        log_success "备份 requirements.txt"
    fi
    
    if [ -f "backend/Dockerfile.prod" ]; then
        cp backend/Dockerfile.prod backups/$timestamp/
        log_success "备份 Dockerfile.prod"
    fi
    
    echo "备份保存在: backups/$timestamp/"
}

# 停止现有服务
stop_existing_services() {
    log_info "停止现有服务..."
    
    if docker-compose -f docker-compose.prod.yml ps -q | grep -q .; then
        docker-compose -f docker-compose.prod.yml down
        log_success "现有服务已停止"
    else
        log_info "没有运行中的服务"
    fi
}

# 清理Docker资源
cleanup_docker() {
    log_info "清理Docker资源..."
    
    # 清理未使用的镜像
    docker image prune -f
    
    # 清理未使用的容器
    docker container prune -f
    
    log_success "Docker资源清理完成"
}

# 阶段1：启动基础服务 (MySQL + Redis)
deploy_stage1() {
    echo -e "\n🔄 阶段1: 启动基础服务 (MySQL + Redis)"
    echo "================================================"
    
    # 启动MySQL
    log_info "启动MySQL服务..."
    docker-compose -f docker-compose.prod.yml up -d mysql
    
    if wait_for_service "mysql" 60; then
        sleep 10  # 额外等待MySQL完全初始化
        check_service_health "mysql"
    else
        log_error "MySQL启动失败，停止部署"
        return 1
    fi
    
    # 启动Redis
    log_info "启动Redis服务..."
    docker-compose -f docker-compose.prod.yml up -d redis
    
    if wait_for_service "redis" 30; then
        check_service_health "redis"
    else
        log_error "Redis启动失败，停止部署"
        return 1
    fi
    
    log_success "阶段1完成：基础服务启动成功"
    return 0
}

# 阶段2：构建并启动Backend服务
deploy_stage2() {
    echo -e "\n🔄 阶段2: 构建并启动Backend服务"
    echo "================================================"
    
    # 构建Backend镜像
    log_info "构建Backend镜像..."
    if docker-compose -f docker-compose.prod.yml build --no-cache backend; then
        log_success "Backend镜像构建成功"
    else
        log_error "Backend镜像构建失败"
        return 1
    fi
    
    # 启动Backend服务
    log_info "启动Backend服务..."
    docker-compose -f docker-compose.prod.yml up -d backend
    
    if wait_for_service "backend" 120; then
        sleep 20  # 等待Backend完全启动
        
        # 测试Backend API
        log_info "测试Backend API..."
        if curl -f http://localhost:8080/ &> /dev/null; then
            log_success "Backend API响应正常"
        else
            log_warn "Backend API测试失败，检查日志"
            check_service_health "backend"
        fi
    else
        log_error "Backend启动失败"
        check_service_health "backend"
        return 1
    fi
    
    log_success "阶段2完成：Backend服务启动成功"
    return 0
}

# 阶段3：启动Nginx服务
deploy_stage3() {
    echo -e "\n🔄 阶段3: 启动Nginx服务"
    echo "================================================"
    
    # 启动Nginx
    log_info "启动Nginx服务..."
    docker-compose -f docker-compose.prod.yml up -d nginx
    
    if wait_for_service "nginx" 30; then
        sleep 5
        
        # 测试前端访问
        log_info "测试前端访问..."
        if curl -f http://localhost/ &> /dev/null; then
            log_success "前端页面访问正常"
        else
            log_warn "前端访问测试失败"
        fi
        
        check_service_health "nginx"
    else
        log_error "Nginx启动失败"
        return 1
    fi
    
    log_success "阶段3完成：Nginx服务启动成功"
    return 0
}

# 最终验证
final_verification() {
    echo -e "\n🔍 最终验证"
    echo "================================================"
    
    # 显示所有服务状态
    log_info "服务状态概览："
    docker-compose -f docker-compose.prod.yml ps
    
    # 资源使用情况
    echo -e "\n📊 资源使用情况："
    docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'
    
    # 系统资源
    echo -e "\n🖥️  系统资源："
    free -h
    
    # API测试
    echo -e "\n🔗 API测试："
    if curl -s http://localhost:8080/ | grep -q "success"; then
        log_success "Backend API正常"
    else
        log_warn "Backend API异常"
    fi
    
    # 前端测试
    if curl -s http://localhost/ | grep -q "html"; then
        log_success "前端页面正常"
    else
        log_warn "前端页面异常"
    fi
    
    echo -e "\n🌐 访问地址："
    echo "  前端: http://localhost/"
    echo "  API:  http://localhost:8080/"
    
    # 获取外部IP
    external_ip=$(curl -s ifconfig.me)
    if [ ! -z "$external_ip" ]; then
        echo "  外部访问: http://$external_ip/"
    fi
}

# 主函数
main() {
    # 检查是否为root用户或有docker权限
    if ! docker ps &> /dev/null; then
        log_error "无法访问Docker，请检查权限或确保Docker服务正在运行"
        exit 1
    fi
    
    # 确认部署
    echo "即将开始分阶段部署，这将："
    echo "1. 停止现有服务"
    echo "2. 备份当前配置"
    echo "3. 分阶段启动服务"
    echo ""
    read -p "确认继续? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "部署已取消"
        exit 0
    fi
    
    # 执行部署步骤
    backup_configs || { log_error "配置备份失败"; exit 1; }
    stop_existing_services
    cleanup_docker
    
    deploy_stage1 || { log_error "阶段1部署失败"; exit 1; }
    deploy_stage2 || { log_error "阶段2部署失败"; exit 1; }
    deploy_stage3 || { log_error "阶段3部署失败"; exit 1; }
    
    final_verification
    
    echo -e "\n🎉 部署完成！"
    echo "=================================="
    log_success "InterviewPro已成功部署并运行"
    log_info "使用 './monitor_resources.sh' 监控系统状态"
    log_info "使用 './emergency_recovery.sh' 进行紧急恢复"
}

# 执行主函数
main "$@" 