#!/bin/bash

# 502错误诊断和修复脚本
# 针对 https://offerott.com/ 的502问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

echo "🔧 InterviewPro 502错误诊断修复工具"
echo "====================================="

# 服务器配置
SERVER_IP="3.14.247.189"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"
SSH_USER="ubuntu"
WEBSITE_URL="https://offerott.com"

# 步骤1：外部访问测试
log "步骤1: 检查外部网站访问状态..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$WEBSITE_URL/" || echo "000")
log "网站HTTP状态码: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "502" ]; then
    error "确认502错误存在"
elif [ "$HTTP_STATUS" = "200" ]; then
    success "网站访问正常，无需修复"
    exit 0
elif [ "$HTTP_STATUS" = "000" ]; then
    error "无法连接到网站"
else
    warn "HTTP状态码: $HTTP_STATUS"
fi

# 步骤2：服务器状态诊断
log "步骤2: 连接服务器进行诊断..."

# 创建远程诊断脚本
REMOTE_SCRIPT="
#!/bin/bash
echo '🔍 === 服务器状态诊断 ==='
echo '--- Docker容器状态 ---'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo
echo '--- 系统Nginx状态 ---'
sudo systemctl status nginx --no-pager || echo 'Nginx服务未运行'
echo
echo '--- 端口监听状态 ---'
sudo netstat -tlnp | grep ':80\|:443\|:5001' || echo '未找到监听端口'
echo
echo '--- Docker网络状态 ---'
docker network ls
echo
echo '--- 检查Nginx容器日志 ---'
docker logs interviewpro-nginx-1 --tail=10 2>/dev/null || echo 'Nginx容器未运行或无日志'
echo
echo '--- 检查后端服务连接 ---'
curl -s http://localhost:5001/api/health || echo '后端服务无响应'
echo
echo '--- SSL证书状态 ---'
sudo ls -la /etc/letsencrypt/live/offerott.com/ 2>/dev/null || echo 'SSL证书目录不存在'
echo
echo '--- Nginx配置文件检查 ---'
sudo nginx -t 2>&1 || echo 'Nginx配置有误'
"

# 执行远程诊断
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "$REMOTE_SCRIPT" > server_diagnosis.log 2>&1

log "诊断结果已保存到 server_diagnosis.log"
echo "============ 诊断结果 ============"
cat server_diagnosis.log
echo "================================="

# 步骤3：分析问题并修复
log "步骤3: 分析问题并执行修复..."

# 检查常见问题
if grep -q "nginx.*not running" server_diagnosis.log || grep -q "nginx.*failed" server_diagnosis.log; then
    warn "发现系统Nginx服务问题"
    NGINX_SYSTEM_ISSUE=true
fi

if grep -q "interviewpro-nginx-1.*Exit" server_diagnosis.log || ! grep -q "interviewpro-nginx-1.*Up" server_diagnosis.log; then
    warn "发现Docker Nginx容器问题"
    NGINX_CONTAINER_ISSUE=true
fi

if ! grep -q ":80.*LISTEN" server_diagnosis.log || ! grep -q ":443.*LISTEN" server_diagnosis.log; then
    warn "发现端口监听问题"
    PORT_ISSUE=true
fi

# 修复脚本
REPAIR_SCRIPT="
#!/bin/bash
echo '🔧 === 开始修复502错误 ==='

# 修复1: 重启Docker容器
echo '--- 重启Docker服务 ---'
cd /home/ubuntu/InterviewPro
docker-compose down
sleep 5
docker-compose up -d

# 修复2: 检查并修复系统Nginx
echo '--- 检查系统Nginx配置 ---'
sudo nginx -t || {
    echo '修复Nginx配置...'
    sudo systemctl reload nginx
}

# 修复3: 确保系统Nginx运行
echo '--- 确保系统Nginx运行 ---'
sudo systemctl start nginx
sudo systemctl enable nginx

# 修复4: 检查Docker容器端口映射
echo '--- 检查Docker端口映射 ---'
docker ps --format 'table {{.Names}}\t{{.Ports}}'

# 修复5: 重新加载Nginx配置
echo '--- 重新加载Nginx配置 ---'
sudo systemctl reload nginx

# 修复6: 检查日志
echo '--- 检查关键日志 ---'
sudo tail -20 /var/log/nginx/error.log || echo '无Nginx错误日志'
docker logs interviewpro-backend-1 --tail=5 || echo '无后端日志'

echo '🎯 修复完成，等待服务稳定...'
sleep 15

echo '--- 最终状态检查 ---'
curl -s http://localhost/ > /dev/null && echo '✅ 本地前端访问正常' || echo '❌ 本地前端访问失败'
curl -s http://localhost:5001/api/health > /dev/null && echo '✅ 后端API访问正常' || echo '❌ 后端API访问失败'
sudo systemctl is-active nginx && echo '✅ 系统Nginx运行正常' || echo '❌ 系统Nginx未运行'
docker ps --filter 'status=running' --format '{{.Names}}' | grep -c interviewpro && echo '✅ Docker容器运行正常' || echo '❌ Docker容器未正常运行'
"

# 执行修复
log "执行修复操作..."
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "$REPAIR_SCRIPT"

# 步骤4：验证修复结果
log "步骤4: 验证修复结果..."
sleep 10

# 重新测试网站访问
NEW_HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "$WEBSITE_URL/" || echo "000")
log "修复后HTTP状态码: $NEW_HTTP_STATUS"

if [ "$NEW_HTTP_STATUS" = "200" ]; then
    success "🎉 502错误修复成功！网站现在可以正常访问"
    
    # 额外验证
    log "进行额外验证..."
    curl -s "$WEBSITE_URL/" | head -20 | grep -q "InterviewPro\|HTML" && success "网站内容正常" || warn "网站内容可能有问题"
    
elif [ "$NEW_HTTP_STATUS" = "502" ]; then
    error "502错误仍然存在，需要进一步诊断"
    warn "建议检查："
    echo "  1. Docker容器是否全部正常运行"
    echo "  2. 后端服务是否正常响应"
    echo "  3. Nginx配置是否正确"
    echo "  4. SSL证书是否有效"
    exit 1
else
    warn "网站状态码为 $NEW_HTTP_STATUS，可能需要进一步检查"
fi

# 清理临时文件
rm -f server_diagnosis.log

success "502错误修复流程完成！"
echo "网站访问地址: $WEBSITE_URL" 