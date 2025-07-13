#!/bin/bash

# InterviewPro 资源监控脚本
# 使用方法: ./monitor_resources.sh [interval]

# 默认监控间隔（秒）
INTERVAL=${1:-10}

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 警告阈值
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90

echo "📊 InterviewPro 资源监控"
echo "=================================="
echo "监控间隔: ${INTERVAL}秒"
echo "警告阈值: CPU ${CPU_THRESHOLD}%, 内存 ${MEMORY_THRESHOLD}%, 磁盘 ${DISK_THRESHOLD}%"
echo "按 Ctrl+C 停止监控"
echo ""

# 获取颜色输出函数
get_color_by_percent() {
    local percent=$1
    local threshold=$2
    
    if [ "$percent" -ge "$threshold" ]; then
        echo "$RED"
    elif [ "$percent" -ge $((threshold - 15)) ]; then
        echo "$YELLOW"
    else
        echo "$GREEN"
    fi
}

# 监控函数
monitor_loop() {
    while true; do
        # 清屏
        clear
        
        echo -e "${CYAN}📊 InterviewPro 资源监控 - $(date)${NC}"
        echo "=================================================================="
        
        # 1. 系统资源概览
        echo -e "\n${BLUE}🖥️  系统资源概览${NC}"
        echo "----------------------------------------"
        
        # 内存使用
        memory_info=$(free | awk 'NR==2{printf "%.0f %.0f %.2f", $3,$2,($3/$2)*100}')
        mem_used=$(echo $memory_info | cut -d' ' -f1)
        mem_total=$(echo $memory_info | cut -d' ' -f2)
        mem_percent=$(echo $memory_info | cut -d' ' -f3 | cut -d'.' -f1)
        
        mem_color=$(get_color_by_percent $mem_percent $MEMORY_THRESHOLD)
        echo -e "内存使用: ${mem_color}${mem_used}MB/${mem_total}MB (${mem_percent}%)${NC}"
        
        # CPU使用
        cpu_percent=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
        cpu_idle=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | sed 's/%id,//')
        cpu_used=$(echo "100 - $cpu_idle" | bc 2>/dev/null || echo "N/A")
        
        if [ "$cpu_used" != "N/A" ]; then
            cpu_used_int=$(echo $cpu_used | cut -d'.' -f1)
            cpu_color=$(get_color_by_percent $cpu_used_int $CPU_THRESHOLD)
            echo -e "CPU使用:  ${cpu_color}${cpu_used}%${NC}"
        else
            echo "CPU使用:  N/A"
        fi
        
        # 磁盘使用
        disk_info=$(df -h . | awk 'NR==2 {print $3,$2,$5}')
        disk_used=$(echo $disk_info | cut -d' ' -f1)
        disk_total=$(echo $disk_info | cut -d' ' -f2)
        disk_percent=$(echo $disk_info | cut -d' ' -f3 | sed 's/%//')
        
        disk_color=$(get_color_by_percent $disk_percent $DISK_THRESHOLD)
        echo -e "磁盘使用: ${disk_color}${disk_used}/${disk_total} (${disk_percent}%)${NC}"
        
        # Swap使用
        swap_info=$(free | awk '/^Swap:/ {if($2>0) printf "%.0f %.0f %.2f", $3,$2,($3/$2)*100; else print "0 0 0"}')
        if [ "$swap_info" != "0 0 0" ]; then
            swap_used=$(echo $swap_info | cut -d' ' -f1)
            swap_total=$(echo $swap_info | cut -d' ' -f2)
            swap_percent=$(echo $swap_info | cut -d' ' -f3 | cut -d'.' -f1)
            echo -e "Swap使用: ${swap_used}MB/${swap_total}MB (${swap_percent}%)"
        else
            echo "Swap使用: 未配置"
        fi
        
        # 2. Docker容器状态
        echo -e "\n${BLUE}🐳 Docker容器状态${NC}"
        echo "----------------------------------------"
        
        if docker-compose -f docker-compose.prod.yml ps &>/dev/null; then
            # 服务状态
            echo "服务状态:"
            docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}"
            
            # 容器资源使用
            echo -e "\n容器资源使用:"
            docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}"
        else
            echo -e "${RED}❌ 无法访问Docker服务${NC}"
        fi
        
        # 3. 网络连接状态
        echo -e "\n${BLUE}🌐 网络连接状态${NC}"
        echo "----------------------------------------"
        
        # 检查关键端口
        ports=(80 3306 6379 8080)
        for port in "${ports[@]}"; do
            if netstat -tuln 2>/dev/null | grep -q ":$port "; then
                echo -e "端口 $port: ${GREEN}✅ 开放${NC}"
            else
                echo -e "端口 $port: ${RED}❌ 关闭${NC}"
            fi
        done
        
        # 4. 应用健康检查
        echo -e "\n${BLUE}🏥 应用健康检查${NC}"
        echo "----------------------------------------"
        
        # Backend API检查
        if curl -f -s http://localhost:8080/ &>/dev/null; then
            echo -e "Backend API: ${GREEN}✅ 正常${NC}"
        else
            echo -e "Backend API: ${RED}❌ 异常${NC}"
        fi
        
        # 前端检查
        if curl -f -s http://localhost/ &>/dev/null; then
            echo -e "前端页面:   ${GREEN}✅ 正常${NC}"
        else
            echo -e "前端页面:   ${RED}❌ 异常${NC}"
        fi
        
        # MySQL连接检查
        if docker-compose -f docker-compose.prod.yml exec -T mysql mysqladmin ping &>/dev/null; then
            echo -e "MySQL连接:  ${GREEN}✅ 正常${NC}"
        else
            echo -e "MySQL连接:  ${RED}❌ 异常${NC}"
        fi
        
        # Redis连接检查
        if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping &>/dev/null; then
            echo -e "Redis连接:  ${GREEN}✅ 正常${NC}"
        else
            echo -e "Redis连接:  ${RED}❌ 异常${NC}"
        fi
        
        # 5. 最近日志错误
        echo -e "\n${BLUE}📋 最近日志 (最新5条)${NC}"
        echo "----------------------------------------"
        
        if docker-compose -f docker-compose.prod.yml ps -q backend &>/dev/null; then
            echo "Backend日志:"
            docker-compose -f docker-compose.prod.yml logs backend --tail=3 2>/dev/null | head -5
        fi
        
        # 6. 警告信息
        warnings=()
        if [ "$mem_percent" -ge "$MEMORY_THRESHOLD" ]; then
            warnings+=("内存使用率过高: ${mem_percent}%")
        fi
        
        if [ "$cpu_used" != "N/A" ] && [ "$cpu_used_int" -ge "$CPU_THRESHOLD" ]; then
            warnings+=("CPU使用率过高: ${cpu_used}%")
        fi
        
        if [ "$disk_percent" -ge "$DISK_THRESHOLD" ]; then
            warnings+=("磁盘使用率过高: ${disk_percent}%")
        fi
        
        if [ ${#warnings[@]} -gt 0 ]; then
            echo -e "\n${RED}⚠️  警告信息${NC}"
            echo "----------------------------------------"
            for warning in "${warnings[@]}"; do
                echo -e "${RED}• $warning${NC}"
            done
        fi
        
        # 底部信息
        echo "=================================================================="
        echo -e "${CYAN}下次更新: $(date -d "+${INTERVAL} seconds")${NC}"
        echo -e "监控间隔: ${INTERVAL}秒 | 按 Ctrl+C 停止"
        
        # 等待
        sleep $INTERVAL
    done
}

# 信号处理
trap 'echo -e "\n\n${CYAN}监控已停止${NC}"; exit 0' INT

# 检查Docker访问权限
if ! docker ps &>/dev/null; then
    echo -e "${RED}❌ 无法访问Docker，请检查权限${NC}"
    exit 1
fi

# 开始监控
monitor_loop 