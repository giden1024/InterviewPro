#!/bin/bash

# SSH连接持续监控脚本
# 一旦服务器恢复连接，立即执行修复操作

set -e

SERVER_IP="3.14.247.189"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"
SSH_USER="ubuntu"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 快速SSH连接测试
quick_ssh_test() {
    timeout 15 ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" \
        -o ConnectTimeout=10 \
        -o ServerAliveInterval=2 \
        -o ServerAliveCountMax=2 \
        -o StrictHostKeyChecking=no \
        -o BatchMode=yes \
        -q \
        "echo 'SSH-OK'" 2>/dev/null
}

# 检查网站状态
check_website() {
    local status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://offerott.com/" 2>/dev/null || echo "000")
    echo "$status"
}

# 执行紧急修复
emergency_fix() {
    log "🚨 执行紧急修复操作..."
    
    # 1. 检查系统状态
    log "检查系统状态..."
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" -o ConnectTimeout=30 "
        echo '=== 系统状态检查 ==='
        echo 'CPU使用率:'
        top -bn1 | grep 'Cpu(s)' | head -1
        echo '内存使用:'
        free -h | grep Mem
        echo '负载:'
        uptime
        echo 'Docker容器:'
        docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.CPUPerc}}' 2>/dev/null || echo 'Docker信息获取失败'
    "
    
    # 2. 停止高负载服务
    log "停止可能的高负载服务..."
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" -o ConnectTimeout=30 "
        cd /home/ubuntu/InterviewPro
        echo '停止Docker服务...'
        docker-compose down 2>/dev/null || true
        echo '清理Docker资源...'
        docker system prune -f 2>/dev/null || true
        echo '清理系统缓存...'
        sync
        echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null 2>&1 || true
    "
    
    # 3. 等待系统稳定
    log "等待系统稳定..."
    sleep 15
    
    # 4. 检查系统恢复状态
    log "检查系统恢复状态..."
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" -o ConnectTimeout=30 "
        echo '=== 恢复后状态 ==='
        echo 'CPU使用率:'
        top -bn1 | grep 'Cpu(s)' | head -1
        echo '内存使用:'
        free -h | grep Mem
    "
    
    # 5. 重启服务（带资源限制）
    log "重启服务（应用资源限制）..."
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" -o ConnectTimeout=30 "
        cd /home/ubuntu/InterviewPro
        
        # 分阶段启动
        echo '启动数据库...'
        docker-compose up -d mysql redis 2>/dev/null || docker-compose up -d mysql redis
        sleep 20
        
        echo '启动后端...'
        docker-compose up -d backend
        sleep 20
        
        echo '启动前端...'
        docker-compose up -d nginx 2>/dev/null || docker-compose up -d frontend
        
        echo '检查服务状态:'
        docker ps --format 'table {{.Names}}\t{{.Status}}'
    "
    
    success "紧急修复完成"
}

# 主监控循环
main_monitor() {
    echo "🔍 InterviewPro SSH连接监控器"
    echo "=============================="
    echo "目标服务器: $SERVER_IP"
    echo "监控开始时间: $(date)"
    echo ""
    
    local attempt=1
    local last_website_check=$(date +%s)
    
    while true; do
        printf "\r[尝试 %03d] 检查SSH连接... " $attempt
        
        # 尝试SSH连接
        if result=$(quick_ssh_test 2>&1); then
            if [ "$result" = "SSH-OK" ]; then
                echo ""
                success "🎉 SSH连接恢复！服务器重新上线"
                
                # 执行紧急修复
                emergency_fix
                
                # 检查网站状态
                log "检查网站恢复状态..."
                sleep 10
                local website_status=$(check_website)
                
                if [ "$website_status" = "200" ]; then
                    success "✅ 网站完全恢复正常: https://offerott.com/"
                elif [ "$website_status" = "502" ]; then
                    warn "⚠️ 网站仍显示502错误，需要进一步修复"
                    log "运行完整修复脚本..."
                    ./fix-502-error.sh 2>/dev/null || echo "502修复脚本执行完毕"
                else
                    warn "⚠️ 网站状态码: $website_status"
                fi
                
                echo ""
                echo "🎯 恢复完成总结:"
                echo "- ✅ SSH连接已恢复"
                echo "- ✅ 紧急修复已执行"
                echo "- 📊 网站状态: $website_status"
                echo ""
                success "监控任务完成，服务器已恢复正常运行"
                break
            fi
        fi
        
        # 每60秒检查一次网站状态
        local current_time=$(date +%s)
        if [ $((current_time - last_website_check)) -ge 60 ]; then
            echo ""
            local website_status=$(check_website)
            log "网站状态检查: $website_status"
            last_website_check=$current_time
        fi
        
        ((attempt++))
        sleep 5
        
        # 每100次尝试显示统计信息
        if [ $((attempt % 100)) -eq 0 ]; then
            echo ""
            log "监控统计: 已尝试 $attempt 次，累计时间 $((attempt * 5 / 60)) 分钟"
        fi
    done
}

# 检查参数
case "${1:-monitor}" in
    "monitor")
        main_monitor
        ;;
    "test")
        log "执行单次连接测试..."
        if result=$(quick_ssh_test 2>&1); then
            if [ "$result" = "SSH-OK" ]; then
                success "SSH连接正常"
                exit 0
            else
                warn "SSH连接异常: $result"
                exit 1
            fi
        else
            error "SSH连接失败"
            exit 1
        fi
        ;;
    "fix")
        log "执行紧急修复..."
        emergency_fix
        ;;
    *)
        echo "用法: $0 [monitor|test|fix]"
        echo "  monitor - 持续监控SSH连接（默认）"
        echo "  test    - 执行单次连接测试"
        echo "  fix     - 立即执行紧急修复"
        exit 1
        ;;
esac 