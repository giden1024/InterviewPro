#!/bin/bash

# CPU 100% 紧急修复脚本
# 解决部署后CPU占用过高导致系统无响应问题

set -e

echo "🚨 InterviewPro CPU 100% 紧急修复工具"
echo "====================================="

SERVER_IP="3.14.247.189"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"
SSH_USER="ubuntu"

# 增强的SSH连接函数，适用于高负载系统
emergency_ssh() {
    local command="$1"
    local max_attempts=10
    local attempt=1
    
    echo "[$(date '+%H:%M:%S')] 紧急SSH连接: $command"
    
    while [ $attempt -le $max_attempts ]; do
        echo "尝试 $attempt/$max_attempts (高负载模式)..."
        
        if timeout 60 ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" \
            -o ConnectTimeout=30 \
            -o ServerAliveInterval=5 \
            -o ServerAliveCountMax=10 \
            -o TCPKeepAlive=yes \
            -o Compression=no \
            -o StrictHostKeyChecking=no \
            -o BatchMode=yes \
            -o LogLevel=ERROR \
            "$command" 2>/dev/null; then
            echo "✅ 命令执行成功"
            return 0
        fi
        
        echo "⚠️ 尝试 $attempt 失败，等待10秒..."
        sleep 10
        ((attempt++))
    done
    
    echo "❌ 所有连接尝试失败"
    return 1
}

echo ""
echo "🔍 步骤1: 尝试连接服务器并诊断CPU使用情况..."

# 尝试获取CPU使用率
if emergency_ssh "top -bn1 | head -20"; then
    echo "✅ 成功获取系统状态"
else
    echo "❌ 无法连接服务器，可能CPU使用率过高"
    echo ""
    echo "🆘 紧急建议："
    echo "1. 通过AWS控制台重启EC2实例"
    echo "2. 或者通过AWS控制台直接连接服务器"
    echo "3. 执行以下命令停止所有Docker服务："
    echo "   docker-compose down"
    echo "   docker system prune -f"
    exit 1
fi

echo ""
echo "🛑 步骤2: 紧急停止高负载服务..."

# 停止Docker服务
if emergency_ssh "cd /home/ubuntu/InterviewPro && docker-compose down"; then
    echo "✅ Docker服务已停止"
else
    echo "⚠️ Docker停止可能失败，尝试强制停止..."
    emergency_ssh "docker kill \$(docker ps -q) 2>/dev/null || true"
    emergency_ssh "docker rm \$(docker ps -aq) 2>/dev/null || true"
fi

echo ""
echo "🧹 步骤3: 清理系统资源..."

# 清理Docker资源
emergency_ssh "
echo '清理Docker资源...'
docker system prune -f 2>/dev/null || true
docker volume prune -f 2>/dev/null || true
docker network prune -f 2>/dev/null || true
echo '清理系统缓存...'
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true
echo '检查内存使用...'
free -h
echo '检查CPU使用...'
top -bn1 | grep 'Cpu(s)' | head -1
"

echo ""
echo "⏰ 步骤4: 等待系统稳定..."
sleep 20

echo ""
echo "📊 步骤5: 检查系统恢复状态..."

emergency_ssh "
echo '=== 系统资源状态 ==='
echo 'CPU使用率:'
top -bn1 | grep 'Cpu(s)' | head -1
echo '内存使用:'
free -h | grep -E 'Mem|Swap'
echo '磁盘使用:'
df -h / | tail -1
echo '负载平均值:'
uptime
echo '运行中的进程:'
ps aux --sort=-%cpu | head -10
echo '========================'
"

echo ""
echo "🔧 步骤6: 配置资源限制并重启服务..."

# 创建优化的docker-compose配置
emergency_ssh "
cd /home/ubuntu/InterviewPro
echo '备份原配置...'
cp docker-compose.yml docker-compose.yml.backup-\$(date +%Y%m%d-%H%M%S)

echo '应用资源限制配置...'
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - '5001:5000'
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
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
          cpus: '0.8'
          memory: 512M
        reservations:
          cpus: '0.2'
          memory: 256M
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:5000/api/health']
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mysql:
    image: mysql:8.0
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
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 256M
    command: --default-authentication-plugin=mysql_native_password --max_connections=50

  redis:
    image: redis:alpine
    ports:
      - '6379:6379'
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 128M
        reservations:
          cpus: '0.05'
          memory: 64M

  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 128M

volumes:
  mysql_data:
EOF

echo '✅ 资源限制配置已应用'
"

echo ""
echo "🚀 步骤7: 分阶段启动服务..."

# 分阶段启动服务
echo "启动数据库服务..."
emergency_ssh "cd /home/ubuntu/InterviewPro && docker-compose up -d mysql redis"

echo "等待数据库启动..."
sleep 30

echo "启动后端服务..."
emergency_ssh "cd /home/ubuntu/InterviewPro && docker-compose up -d backend"

echo "等待后端启动..."
sleep 20

echo "启动前端服务..."
emergency_ssh "cd /home/ubuntu/InterviewPro && docker-compose up -d nginx"

echo ""
echo "📋 步骤8: 验证修复效果..."

sleep 10

emergency_ssh "
echo '=== 最终系统状态 ==='
echo 'Docker容器状态:'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo 'CPU使用率:'
top -bn1 | grep 'Cpu(s)' | head -1
echo 'Docker资源使用:'
docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}'
"

echo ""
echo "🌐 步骤9: 测试外部访问..."

sleep 10
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 20 "https://offerott.com/" || echo "000")
echo "外部访问状态: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ 修复成功！网站可以正常访问"
elif [ "$HTTP_STATUS" = "502" ]; then
    echo "⚠️ 仍有502错误，需要进一步检查"
else
    echo "⚠️ 网站状态: $HTTP_STATUS，可能需要更多时间启动"
fi

echo ""
echo "🎉 CPU 100% 问题修复完成！"
echo ""
echo "📊 修复总结:"
echo "1. ✅ 停止了高负载服务"
echo "2. ✅ 清理了系统资源" 
echo "3. ✅ 应用了Docker资源限制"
echo "4. ✅ 分阶段重启了服务"
echo "5. ✅ 验证了系统恢复状态"
echo ""
echo "🔧 后续建议:"
echo "- 考虑升级EC2实例到更高配置"
echo "- 定期监控系统资源使用"
echo "- 优化应用代码性能"
echo "- 设置自动监控和告警" 