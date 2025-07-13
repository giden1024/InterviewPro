#!/bin/bash

# ============================================
# InterviewPro 部署前检查脚本
# 检查代码同步、环境配置、依赖项等
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

# 检查结果统计
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    ((FAILED_CHECKS++))
}

success() {
    echo -e "${GREEN}[PASS] $1${NC}"
    ((PASSED_CHECKS++))
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
    ((WARNING_CHECKS++))
}

check_item() {
    ((TOTAL_CHECKS++))
}

# 检查本地环境
check_local_environment() {
    log "🔍 检查本地环境..."
    
    # 检查必要工具
    check_item
    if command -v git &> /dev/null; then
        success "Git 已安装"
    else
        error "Git 未安装"
    fi
    
    check_item
    if command -v docker &> /dev/null; then
        success "Docker 已安装"
    else
        error "Docker 未安装"
    fi
    
    check_item
    if command -v npm &> /dev/null; then
        success "NPM 已安装 ($(npm --version))"
    else
        error "NPM 未安装"
    fi
    
    check_item
    if command -v node &> /dev/null; then
        success "Node.js 已安装 ($(node --version))"
    else
        error "Node.js 未安装"
    fi
    
    # 检查项目目录结构
    check_item
    if [ -d "frontend" ] && [ -d "backend" ]; then
        success "项目目录结构正确"
    else
        error "项目目录结构不正确，请在项目根目录执行"
    fi
    
    # 检查关键文件
    local key_files=("package.json" "docker-compose.prod.yml" "$KEY_FILE")
    for file in "${key_files[@]}"; do
        check_item
        if [ -f "$file" ] || [ -f "frontend/$file" ] || [ -f "backend/$file" ]; then
            success "关键文件存在: $file"
        else
            if [ "$file" == "$KEY_FILE" ]; then
                error "SSH密钥文件不存在: $file"
            else
                warning "关键文件可能缺失: $file"
            fi
        fi
    done
}

# 检查Git状态
check_git_status() {
    log "📋 检查Git状态..."
    
    # 检查是否在Git仓库中
    check_item
    if git rev-parse --git-dir > /dev/null 2>&1; then
        success "当前目录是Git仓库"
    else
        error "当前目录不是Git仓库"
        return
    fi
    
    # 检查当前分支
    check_item
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" == "main" ] || [ "$current_branch" == "master" ]; then
        success "当前在主分支: $current_branch"
    else
        warning "当前不在主分支: $current_branch"
    fi
    
    # 检查未提交的更改
    check_item
    if git diff --quiet && git diff --cached --quiet; then
        success "没有未提交的更改"
    else
        warning "存在未提交的更改："
        git diff --stat
        git diff --cached --stat
    fi
    
    # 检查与远程的同步状态
    check_item
    git fetch origin main &>/dev/null
    local local_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/main)
    
    if [ "$local_commit" == "$remote_commit" ]; then
        success "本地与远程同步"
    else
        warning "本地与远程不同步"
        echo "  本地提交: $local_commit"
        echo "  远程提交: $remote_commit"
        echo "  差异: $(git rev-list HEAD...origin/main --count) 个提交"
    fi
    
    # 检查最近的提交
    check_item
    local last_commit_time=$(git log -1 --format=%ct)
    local current_time=$(date +%s)
    local time_diff=$((current_time - last_commit_time))
    local days_ago=$((time_diff / 86400))
    
    if [ $days_ago -le 7 ]; then
        success "最近有活跃开发 ($days_ago 天前)"
    else
        warning "最后提交较久 ($days_ago 天前)"
    fi
}

# 检查前端项目
check_frontend() {
    log "📦 检查前端项目..."
    
    if [ ! -d "frontend" ]; then
        error "前端目录不存在"
        return
    fi
    
    cd frontend
    
    # 检查package.json
    check_item
    if [ -f "package.json" ]; then
        success "package.json 存在"
    else
        error "package.json 不存在"
        cd ..
        return
    fi
    
    # 检查依赖安装
    check_item
    if [ -d "node_modules" ]; then
        success "node_modules 存在"
    else
        warning "node_modules 不存在，需要安装依赖"
    fi
    
    # 检查构建脚本
    check_item
    if grep -q '"build"' package.json; then
        success "构建脚本已配置"
    else
        error "构建脚本未配置"
    fi
    
    # 尝试依赖检查
    check_item
    if npm list --depth=0 &>/dev/null; then
        success "NPM 依赖完整"
    else
        warning "NPM 依赖可能有问题"
    fi
    
    # 检查TypeScript配置
    check_item
    if [ -f "tsconfig.json" ]; then
        success "TypeScript 配置存在"
    else
        warning "TypeScript 配置不存在"
    fi
    
    cd ..
}

# 检查后端项目
check_backend() {
    log "🐍 检查后端项目..."
    
    if [ ! -d "backend" ]; then
        error "后端目录不存在"
        return
    fi
    
    cd backend
    
    # 检查requirements.txt
    check_item
    if [ -f "requirements.txt" ]; then
        success "requirements.txt 存在"
    else
        error "requirements.txt 不存在"
    fi
    
    # 检查Dockerfile
    check_item
    if [ -f "Dockerfile" ] || [ -f "Dockerfile.prod" ]; then
        success "Dockerfile 存在"
    else
        warning "Dockerfile 不存在"
    fi
    
    # 检查主应用文件
    check_item
    if [ -f "run.py" ] || [ -f "run_complete.py" ] || [ -f "app.py" ]; then
        success "主应用文件存在"
    else
        error "主应用文件不存在"
    fi
    
    # 检查虚拟环境
    check_item
    if [ -d "venv" ] || [ -d ".venv" ]; then
        success "Python虚拟环境存在"
    else
        warning "Python虚拟环境不存在"
    fi
    
    cd ..
}

# 检查Docker配置
check_docker_config() {
    log "🐳 检查Docker配置..."
    
    # 检查docker-compose.prod.yml
    check_item
    if [ -f "docker-compose.prod.yml" ]; then
        success "docker-compose.prod.yml 存在"
        
        # 检查服务配置
        check_item
        if grep -q "backend:" docker-compose.prod.yml && grep -q "frontend:" docker-compose.prod.yml; then
            success "Docker服务配置完整"
        else
            warning "Docker服务配置可能不完整"
        fi
        
        # 检查端口配置
        check_item
        if grep -q "ports:" docker-compose.prod.yml; then
            success "端口配置存在"
        else
            warning "端口配置可能缺失"
        fi
        
    else
        error "docker-compose.prod.yml 不存在"
    fi
    
    # 检查Docker服务状态
    check_item
    if docker info &>/dev/null; then
        success "Docker 服务运行正常"
    else
        error "Docker 服务未运行或无权限"
    fi
}

# 检查环境配置
check_environment_config() {
    log "⚙️ 检查环境配置..."
    
    # 检查环境变量模板
    check_item
    if [ -f "env.production.template" ] || [ -f ".env.production.template" ]; then
        success "生产环境配置模板存在"
    else
        warning "生产环境配置模板不存在"
    fi
    
    # 检查本地环境配置
    check_item
    if [ -f ".env" ] || [ -f ".env.local" ]; then
        success "本地环境配置存在"
    else
        warning "本地环境配置不存在"
    fi
    
    # 检查必要的环境变量
    local required_vars=("DATABASE_URL" "JWT_SECRET_KEY" "CORS_ORIGINS")
    for var in "${required_vars[@]}"; do
        check_item
        if grep -q "$var" env.production.template 2>/dev/null || grep -q "$var" .env.production.template 2>/dev/null; then
            success "环境变量模板包含: $var"
        else
            warning "环境变量模板缺少: $var"
        fi
    done
}

# 检查服务器连接和状态
check_server_connection() {
    log "🌐 检查服务器连接..."
    
    # 检查SSH密钥
    check_item
    if [ -f "$KEY_FILE" ]; then
        success "SSH密钥文件存在"
        
        # 检查密钥权限
        check_item
        local key_permissions=$(stat -c "%a" "$KEY_FILE")
        if [ "$key_permissions" == "600" ]; then
            success "SSH密钥权限正确 (600)"
        else
            warning "SSH密钥权限不正确 ($key_permissions)，应该是 600"
        fi
    else
        error "SSH密钥文件不存在: $KEY_FILE"
        return
    fi
    
    # 测试SSH连接
    check_item
    if ssh -i "$KEY_FILE" -o ConnectTimeout=10 "$REMOTE_USER@$SERVER_IP" "echo 'SSH连接成功'" &>/dev/null; then
        success "SSH连接正常"
    else
        error "SSH连接失败"
        return
    fi
    
    # 检查服务器基础信息
    local server_info=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        echo 'OS: '$(lsb_release -d 2>/dev/null | cut -f2 || echo 'Unknown')
        echo 'Uptime: '$(uptime | awk '{print \$3, \$4}' | sed 's/,//')
        echo 'Disk: '$(df -h /home/ubuntu | awk 'NR==2 {print \$4\" available\"}')
        echo 'Memory: '$(free -h | awk 'NR==2{printf \"%.1f/%.1fGB\", \$3/1024, \$2/1024}')
    " 2>/dev/null)
    
    if [ -n "$server_info" ]; then
        success "服务器状态正常"
        echo "$server_info" | sed 's/^/    /'
    else
        warning "无法获取服务器状态信息"
    fi
}

# 检查服务器项目状态
check_server_project() {
    log "📂 检查服务器项目状态..."
    
    if [ ! -f "$KEY_FILE" ]; then
        error "SSH密钥不存在，跳过服务器项目检查"
        return
    fi
    
    # 检查项目目录
    check_item
    local project_exists=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "[ -d '$REMOTE_PATH' ] && echo 'exists' || echo 'missing'" 2>/dev/null)
    
    if [ "$project_exists" == "exists" ]; then
        success "服务器项目目录存在"
    else
        warning "服务器项目目录不存在"
        return
    fi
    
    # 检查Docker状态
    check_item
    local docker_status=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd '$REMOTE_PATH' && docker-compose -f docker-compose.prod.yml ps --format 'table' 2>/dev/null | grep -E '(Up|running)' | wc -l
    " 2>/dev/null)
    
    if [ "$docker_status" -gt 0 ]; then
        success "Docker容器正在运行 ($docker_status 个)"
    else
        warning "没有Docker容器在运行"
    fi
    
    # 检查Git状态（如果存在）
    check_item
    local git_status=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd '$REMOTE_PATH' && git log -1 --format='%h %s' 2>/dev/null || echo 'no git'
    " 2>/dev/null)
    
    if [ "$git_status" != "no git" ]; then
        success "服务器Git状态: $git_status"
    else
        warning "服务器项目不是Git仓库"
    fi
}

# 生成检查报告
generate_report() {
    echo ""
    log "📊 检查报告生成..."
    echo ""
    echo "======================================"
    echo "         部署前检查报告"
    echo "======================================"
    echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "检查项目: InterviewPro"
    echo ""
    echo "检查统计:"
    echo "  总检查项: $TOTAL_CHECKS"
    echo "  通过: $PASSED_CHECKS"
    echo "  失败: $FAILED_CHECKS"
    echo "  警告: $WARNING_CHECKS"
    echo ""
    
    # 计算通过率
    local pass_rate=0
    if [ $TOTAL_CHECKS -gt 0 ]; then
        pass_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    fi
    
    echo "通过率: $pass_rate%"
    echo ""
    
    # 建议
    if [ $FAILED_CHECKS -eq 0 ] && [ $WARNING_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✅ 建议: 所有检查都通过，可以安全部署${NC}"
    elif [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${YELLOW}⚠️  建议: 存在警告项，建议修复后部署${NC}"
    else
        echo -e "${RED}❌ 建议: 存在严重问题，必须修复后才能部署${NC}"
    fi
    
    echo "======================================"
}

# 主函数
main() {
    log "🚀 开始部署前检查..."
    echo ""
    
    # 执行各项检查
    check_local_environment
    echo ""
    check_git_status
    echo ""
    check_frontend
    echo ""
    check_backend
    echo ""
    check_docker_config
    echo ""
    check_environment_config
    echo ""
    check_server_connection
    echo ""
    check_server_project
    
    # 生成报告
    generate_report
    
    # 返回适当的退出码
    if [ $FAILED_CHECKS -gt 0 ]; then
        exit 1
    elif [ $WARNING_CHECKS -gt 0 ]; then
        exit 2
    else
        exit 0
    fi
}

# 如果直接运行脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 