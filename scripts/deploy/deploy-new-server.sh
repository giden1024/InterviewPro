#!/bin/bash

# InterviewPro 新服务器安全部署脚本
# 针对1GB内存实例，严格资源控制

set -e

# 新服务器配置
SERVER_IP="18.219.240.36"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"
SSH_USER="ec2-user"
PROJECT_NAME="InterviewPro"
REMOTE_PATH="/home/$SSH_USER/$PROJECT_NAME"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 生成唯一的部署ID
DEPLOY_ID="new_deploy_$(date +%Y%m%d_%H%M%S)"

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 安全SSH连接函数
safe_ssh() {
    local command="$1"
    local timeout="${2:-30}"
    
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" \
        -o ConnectTimeout="$timeout" \
        -o ServerAliveInterval=10 \
        -o ServerAliveCountMax=3 \
        -o StrictHostKeyChecking=no \
        -o BatchMode=yes \
        "$command"
}

# 检查系统资源
check_system_resources() {
    log "📊 检查系统资源状态..."
    
    local cpu_usage=$(safe_ssh "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1 | tr -d ' ,'" 10)
    local mem_usage=$(safe_ssh "free | grep Mem | awk '{printf \"%.1f\", \$3/\$2 * 100.0}'" 10)
    local load_avg=$(safe_ssh "uptime | awk '{print \$(NF-2)}' | tr -d ','" 10)
    
    log "CPU使用率: ${cpu_usage}%"
    log "内存使用率: ${mem_usage}%"
    log "负载平均值: ${load_avg}"
    
    # 安全检查
    if (( $(echo "$cpu_usage > 50" | bc -l 2>/dev/null || echo 0) )); then
        error "CPU使用率过高 (${cpu_usage}%)，停止部署"
        return 1
    fi
    
    if (( $(echo "$mem_usage > 70" | bc -l 2>/dev/null || echo 0) )); then
        error "内存使用率过高 (${mem_usage}%)，停止部署"
        return 1
    fi
    
    success "系统资源状态正常"
}

# 安装必要软件
install_dependencies() {
    log "📦 安装必要软件..."
    
    safe_ssh "
        echo '更新系统包...'
        sudo dnf update -y
        
        echo '安装Docker...'
        sudo dnf install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $SSH_USER
        
        echo '安装Docker Compose...'
        sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        echo '安装其他工具...'
        sudo dnf install -y git curl nano htop bc
        
        echo '验证安装...'
        docker --version
        docker-compose --version
    " 60
    
    success "软件安装完成"
}

# 上传代码
upload_code() {
    log "📂 上传项目代码..."
    
    # 清理本地临时文件
    rm -f interviewpro-new-server.tar.gz
    
    # 打包代码（排除不需要的文件）
    tar --exclude='node_modules' \
        --exclude='.git' \
        --exclude='backend/venv' \
        --exclude='backend/__pycache__' \
        --exclude='backend/logs' \
        --exclude='frontend/dist' \
        --exclude='*.log' \
        --exclude='*.tar.gz' \
        -czf interviewpro-new-server.tar.gz .
    
    # 上传到服务器
    scp -i "$SSH_KEY" \
        -o StrictHostKeyChecking=no \
        interviewpro-new-server.tar.gz \
        "$SSH_USER@$SERVER_IP:/home/$SSH_USER/"
    
    # 解压代码
    safe_ssh "
        echo '创建项目目录...'
        mkdir -p $REMOTE_PATH
        cd /home/$SSH_USER
        echo '解压项目文件...'
        tar -xzf interviewpro-new-server.tar.gz -C $REMOTE_PATH
        rm interviewpro-new-server.tar.gz
        echo '设置权限...'
        chmod +x $REMOTE_PATH/*.sh 2>/dev/null || true
    " 30
    
    # 清理本地临时文件
    rm -f interviewpro-new-server.tar.gz
    
    success "代码上传完成"
}

# 创建优化的Docker配置
create_optimized_docker_config() {
    log "🔧 创建资源优化的Docker配置..."
    
    safe_ssh "
        cd $REMOTE_PATH
        
        echo '创建优化的docker-compose.yml...'
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: interviewpro-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: interviewpro
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    ports:
      - '3306:3306'
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 256M
        reservations:
          cpus: '0.1'
          memory: 128M
    command: >
      --default-authentication-plugin=mysql_native_password
      --max_connections=20
      --innodb_buffer_pool_size=64M
      --key_buffer_size=8M
      --query_cache_size=0
      --query_cache_type=0

  redis:
    image: redis:alpine
    container_name: interviewpro-redis
    ports:
      - '6379:6379'
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.1'
          memory: 64M
        reservations:
          cpus: '0.05'
          memory: 32M
    command: redis-server --maxmemory 32mb --maxmemory-policy allkeys-lru

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: interviewpro-backend
    ports:
      - '5001:5000'
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
      - WORKERS=1
      - THREADS=2
    volumes:
      - ./backend:/app
      - ./backend/uploads:/app/uploads
      - ./backend/instance:/app/instance
    depends_on:
      - mysql
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.4'
          memory: 384M
        reservations:
          cpus: '0.2'
          memory: 192M
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:5000/api/health']
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  nginx:
    image: nginx:alpine
    container_name: interviewpro-nginx
    ports:
      - '80:80'
    volumes:
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 128M
        reservations:
          cpus: '0.05'
          memory: 64M

volumes:
  mysql_data:
EOF

        echo '创建nginx配置...'
        cat > nginx.conf << 'EOF'
events {
    worker_connections 512;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    client_max_body_size 10M;
    
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    server {
        listen 80;
        server_name _;
        
        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
            try_files \$uri \$uri/ /index.html;
        }
        
        location /api/ {
            proxy_pass http://backend:5000/api/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
    }
}
EOF

        echo '✅ 优化配置创建完成'
    " 30
    
    success "Docker配置优化完成"
}

# 构建前端
build_frontend() {
    log "🏗️ 构建前端..."
    
    # 检查本地是否有dist目录
    if [ ! -d "frontend/dist" ]; then
        log "本地构建前端..."
        cd frontend
        npm install --legacy-peer-deps
        npm run build
        cd ..
    fi
    
    # 上传前端构建结果
    log "上传前端构建文件..."
    tar -czf frontend-dist.tar.gz -C frontend/dist .
    
    scp -i "$SSH_KEY" \
        -o StrictHostKeyChecking=no \
        frontend-dist.tar.gz \
        "$SSH_USER@$SERVER_IP:/home/$SSH_USER/"
    
    safe_ssh "
        cd $REMOTE_PATH
        mkdir -p frontend/dist
        cd frontend/dist
        tar -xzf /home/$SSH_USER/frontend-dist.tar.gz
        rm /home/$SSH_USER/frontend-dist.tar.gz
    " 30
    
    rm -f frontend-dist.tar.gz
    
    success "前端构建完成"
}

# 分阶段启动服务
start_services_staged() {
    log "🚀 分阶段启动服务..."
    
    # 阶段1: 启动数据库
    log "阶段1: 启动数据库服务..."
    safe_ssh "
        cd $REMOTE_PATH
        docker-compose up -d mysql redis
        echo '等待数据库初始化...'
        sleep 30
        docker-compose ps
    " 60
    
    # 检查CPU使用率
    check_system_resources
    
    # 阶段2: 启动后端
    log "阶段2: 启动后端服务..."
    safe_ssh "
        cd $REMOTE_PATH
        docker-compose up -d backend
        echo '等待后端启动...'
        sleep 30
        docker-compose ps
    " 60
    
    # 再次检查资源
    check_system_resources
    
    # 阶段3: 启动前端
    log "阶段3: 启动前端服务..."
    safe_ssh "
        cd $REMOTE_PATH
        docker-compose up -d nginx
        echo '等待前端启动...'
        sleep 20
        docker-compose ps
    " 60
    
    success "所有服务启动完成"
}

# 健康检查
health_check() {
    log "🏥 执行健康检查..."
    
    # 检查容器状态
    safe_ssh "
        cd $REMOTE_PATH
        echo '=== 容器状态 ==='
        docker-compose ps
        
        echo '=== 系统资源使用 ==='
        echo 'CPU使用率:'
        top -bn1 | grep 'Cpu(s)' | head -1
        echo '内存使用:'
        free -h | grep Mem
        echo '容器资源:'
        timeout 10 docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}' || echo '容器统计超时'
        
        echo '=== 服务连接测试 ==='
        curl -s http://localhost/ > /dev/null && echo '✅ 前端正常' || echo '❌ 前端异常'
        curl -s http://localhost:5001/api/health > /dev/null && echo '✅ 后端正常' || echo '❌ 后端异常'
    " 30
    
    # 外部访问测试
    log "测试外部访问..."
    sleep 10
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "http://$SERVER_IP/" 2>/dev/null || echo "000")
    
    if [ "$http_status" = "200" ]; then
        success "✅ 外部访问正常: http://$SERVER_IP/"
    else
        warning "⚠️ 外部访问状态码: $http_status"
    fi
    
    success "健康检查完成"
}

# 主函数
main() {
    echo "🚀 InterviewPro 新服务器安全部署"
    echo "=================================="
    echo "目标服务器: $SERVER_IP"
    echo "部署ID: $DEPLOY_ID"
    echo ""
    
    # 设置错误处理
    trap 'error "部署过程中发生错误，请检查系统状态"; exit 1' ERR
    
    # 执行部署步骤
    check_system_resources
    install_dependencies
    upload_code
    create_optimized_docker_config
    build_frontend
    start_services_staged
    health_check
    
    echo ""
    success "🎉 新服务器部署完成！"
    echo ""
    echo "📊 访问信息:"
    echo "  - 网站: http://$SERVER_IP/"
    echo "  - API: http://$SERVER_IP:5001/api/"
    echo ""
    echo "🔧 管理命令:"
    echo "  - 查看状态: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'cd $REMOTE_PATH && docker-compose ps'"
    echo "  - 查看日志: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'cd $REMOTE_PATH && docker-compose logs'"
    echo "  - 重启服务: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'cd $REMOTE_PATH && docker-compose restart'"
    echo ""
    echo "部署ID: $DEPLOY_ID"
}

# 执行主函数
main "$@" 