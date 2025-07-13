#!/bin/bash

# InterviewPro Log Monitoring Script
# 功能：监控系统日志、应用日志，发现异常并报告

set -e

# 配置变量
LOG_DIR="/home/ec2-user/logs"
MONITOR_LOG="$LOG_DIR/monitor.log"
ALERT_LOG="$LOG_DIR/alerts.log"
REPORT_DIR="/home/ec2-user/reports"
DATE=$(date '+%Y-%m-%d_%H-%M-%S')

# 日志文件路径
BACKEND_LOG="/home/ec2-user/backend/logs"
NGINX_ACCESS_LOG="/var/log/nginx/access.log"
NGINX_ERROR_LOG="/var/log/nginx/error.log"
SYSTEM_LOG="/var/log/messages"

# 监控配置
ERROR_KEYWORDS=("ERROR" "FATAL" "CRITICAL" "Exception" "Traceback" "500" "502" "503" "504")
WARNING_KEYWORDS=("WARNING" "WARN" "404" "401" "403")
MYSQL_ERROR_KEYWORDS=("connection refused" "access denied" "lost connection")

# 创建必要目录
create_directories() {
    mkdir -p "$LOG_DIR" "$REPORT_DIR"
    touch "$MONITOR_LOG" "$ALERT_LOG"
}

# 记录监控日志
log_message() {
    local level=$1
    local message=$2
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $message" | tee -a "$MONITOR_LOG"
}

# 发送告警
send_alert() {
    local severity=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$severity] $message" | tee -a "$ALERT_LOG"
    log_message "ALERT" "[$severity] $message"
    
    # 这里可以添加邮件、Slack或其他通知方式
    # 例如：echo "$message" | mail -s "InterviewPro Alert: $severity" admin@example.com
}

# 检查Docker容器状态
check_docker_containers() {
    log_message "INFO" "检查Docker容器状态..."
    
    local containers=("interviewpro-mysql" "ec2-user-redis-1" "ec2-user-backend-1" "ec2-user-nginx-1")
    local unhealthy_containers=()
    
    for container in "${containers[@]}"; do
        if ! docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
            unhealthy_containers+=("$container")
            send_alert "CRITICAL" "容器停止运行: $container"
        else
            # 检查容器健康状态
            local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")
            if [[ "$health" == "unhealthy" ]]; then
                unhealthy_containers+=("$container (unhealthy)")
                send_alert "WARNING" "容器健康检查失败: $container"
            fi
        fi
    done
    
    if [ ${#unhealthy_containers[@]} -eq 0 ]; then
        log_message "INFO" "所有Docker容器运行正常"
    else
        log_message "ERROR" "发现问题容器: ${unhealthy_containers[*]}"
    fi
}

# 检查磁盘空间
check_disk_space() {
    log_message "INFO" "检查磁盘空间..."
    
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    local available_space=$(df -h / | awk 'NR==2 {print $4}')
    
    if [ "$disk_usage" -gt 90 ]; then
        send_alert "CRITICAL" "磁盘空间严重不足: 使用率${disk_usage}%, 剩余${available_space}"
    elif [ "$disk_usage" -gt 80 ]; then
        send_alert "WARNING" "磁盘空间不足: 使用率${disk_usage}%, 剩余${available_space}"
    else
        log_message "INFO" "磁盘空间正常: 使用率${disk_usage}%, 剩余${available_space}"
    fi
}

# 检查内存使用
check_memory_usage() {
    log_message "INFO" "检查内存使用..."
    
    local memory_info=$(free | awk 'NR==2{printf "%.1f", $3/$2*100}')
    local memory_usage=${memory_info%.*}
    
    if [ "$memory_usage" -gt 90 ]; then
        send_alert "CRITICAL" "内存使用率过高: ${memory_usage}%"
    elif [ "$memory_usage" -gt 80 ]; then
        send_alert "WARNING" "内存使用率较高: ${memory_usage}%"
    else
        log_message "INFO" "内存使用正常: ${memory_usage}%"
    fi
}

# 检查CPU使用率
check_cpu_usage() {
    log_message "INFO" "检查CPU使用率..."
    
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    cpu_usage=${cpu_usage%.*}
    
    if [ "$cpu_usage" -gt 90 ]; then
        send_alert "CRITICAL" "CPU使用率过高: ${cpu_usage}%"
    elif [ "$cpu_usage" -gt 80 ]; then
        send_alert "WARNING" "CPU使用率较高: ${cpu_usage}%"
    else
        log_message "INFO" "CPU使用正常: ${cpu_usage}%"
    fi
}

# 分析后端日志
analyze_backend_logs() {
    log_message "INFO" "分析后端应用日志..."
    
    if [ ! -d "$BACKEND_LOG" ]; then
        log_message "WARNING" "后端日志目录不存在: $BACKEND_LOG"
        return
    fi
    
    # 查找最近5分钟的错误
    local recent_errors=$(find "$BACKEND_LOG" -name "*.log" -mmin -5 -exec grep -l "ERROR\|CRITICAL\|Exception" {} \; 2>/dev/null)
    
    if [ -n "$recent_errors" ]; then
        local error_count=$(echo "$recent_errors" | wc -l)
        send_alert "WARNING" "发现${error_count}个后端日志文件包含错误"
        
        # 详细分析错误
        echo "$recent_errors" | while read -r logfile; do
            local errors=$(grep -E "ERROR|CRITICAL|Exception" "$logfile" | tail -5)
            if [ -n "$errors" ]; then
                log_message "ERROR" "后端错误详情 (${logfile}):"
                echo "$errors" | while read -r error_line; do
                    log_message "ERROR" "  $error_line"
                done
            fi
        done
    else
        log_message "INFO" "后端日志中未发现最近错误"
    fi
}

# 分析Nginx日志
analyze_nginx_logs() {
    log_message "INFO" "分析Nginx访问日志..."
    
    # 检查Nginx错误日志
    if [ -f "$NGINX_ERROR_LOG" ]; then
        local recent_errors=$(tail -100 "$NGINX_ERROR_LOG" | grep "$(date '+%Y/%m/%d %H:')" | wc -l)
        if [ "$recent_errors" -gt 10 ]; then
            send_alert "WARNING" "Nginx在过去1小时内有${recent_errors}个错误"
        fi
    fi
    
    # 检查访问日志中的错误状态码
    if [ -f "$NGINX_ACCESS_LOG" ]; then
        local error_5xx=$(tail -1000 "$NGINX_ACCESS_LOG" | grep -c ' 5[0-9][0-9] ' || echo "0")
        local error_4xx=$(tail -1000 "$NGINX_ACCESS_LOG" | grep -c ' 4[0-9][0-9] ' || echo "0")
        
        if [ "$error_5xx" -gt 50 ]; then
            send_alert "CRITICAL" "检测到大量5xx错误: ${error_5xx}个"
        elif [ "$error_5xx" -gt 20 ]; then
            send_alert "WARNING" "检测到较多5xx错误: ${error_5xx}个"
        fi
        
        if [ "$error_4xx" -gt 100 ]; then
            send_alert "WARNING" "检测到大量4xx错误: ${error_4xx}个"
        fi
        
        log_message "INFO" "Nginx状态统计: 4xx错误${error_4xx}个, 5xx错误${error_5xx}个"
    fi
}

# 检查数据库连接
check_database_connection() {
    log_message "INFO" "检查数据库连接..."
    
    if docker exec interviewpro-mysql mysql -u user -p'password' -e "SELECT 1;" > /dev/null 2>&1; then
        log_message "INFO" "数据库连接正常"
    else
        send_alert "CRITICAL" "无法连接到MySQL数据库"
    fi
}

# 检查SSL证书状态
check_ssl_certificate() {
    log_message "INFO" "检查SSL证书状态..."
    
    local cert_file="/etc/letsencrypt/live/offerott.com/fullchain.pem"
    
    if [ -f "$cert_file" ]; then
        local expiry_date=$(sudo openssl x509 -in "$cert_file" -noout -dates | grep "notAfter" | cut -d= -f2)
        local expiry_timestamp=$(date -d "$expiry_date" +%s)
        local current_timestamp=$(date +%s)
        local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
        
        if [ "$days_until_expiry" -lt 7 ]; then
            send_alert "CRITICAL" "SSL证书将在${days_until_expiry}天后过期"
        elif [ "$days_until_expiry" -lt 30 ]; then
            send_alert "WARNING" "SSL证书将在${days_until_expiry}天后过期"
        else
            log_message "INFO" "SSL证书状态正常，${days_until_expiry}天后过期"
        fi
    else
        send_alert "CRITICAL" "SSL证书文件不存在"
    fi
}

# 生成监控报告
generate_report() {
    local report_file="$REPORT_DIR/monitoring_report_${DATE}.txt"
    
    log_message "INFO" "生成监控报告: $report_file"
    
    cat > "$report_file" << EOF
InterviewPro 系统监控报告
生成时间: $(date '+%Y-%m-%d %H:%M:%S')
======================================================

系统状态概览:
$(docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}')

资源使用情况:
CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
内存使用: $(free -h | awk 'NR==2{printf "使用: %s/%s (%.1f%%)", $3,$2,$3/$2*100}')
磁盘使用: $(df -h / | awk 'NR==2{printf "使用: %s/%s (%s)", $3,$2,$5}')

最近告警 (最近24小时):
$(tail -50 "$ALERT_LOG" | grep "$(date '+%Y-%m-%d')" || echo "无告警")

数据库备份状态:
$(ls -lh /home/ec2-user/backups/mysql/ | tail -5 || echo "无备份文件")

SSL证书状态:
$(sudo openssl x509 -in /etc/letsencrypt/live/offerott.com/fullchain.pem -noout -dates 2>/dev/null || echo "证书文件不存在")

======================================================
EOF

    log_message "INFO" "监控报告已保存到: $report_file"
}

# 清理旧日志和报告
cleanup_old_files() {
    log_message "INFO" "清理旧文件..."
    
    # 清理7天前的监控日志
    find "$LOG_DIR" -name "monitor_*.log" -mtime +7 -delete 2>/dev/null || true
    
    # 清理30天前的报告
    find "$REPORT_DIR" -name "monitoring_report_*.txt" -mtime +30 -delete 2>/dev/null || true
    
    # 压缩大日志文件
    if [ -f "$MONITOR_LOG" ] && [ $(stat -c%s "$MONITOR_LOG") -gt 10485760 ]; then  # 10MB
        gzip "$MONITOR_LOG"
        touch "$MONITOR_LOG"
        log_message "INFO" "监控日志已压缩"
    fi
}

# 主执行函数
main() {
    log_message "INFO" "===== 开始系统监控任务 ====="
    
    create_directories
    
    # 执行各项检查
    check_docker_containers
    check_disk_space
    check_memory_usage
    check_cpu_usage
    check_database_connection
    check_ssl_certificate
    analyze_backend_logs
    analyze_nginx_logs
    
    # 生成报告和清理
    generate_report
    cleanup_old_files
    
    log_message "INFO" "===== 系统监控任务完成 ====="
    
    # 显示告警摘要
    local alert_count=$(grep "$(date '+%Y-%m-%d')" "$ALERT_LOG" | wc -l)
    if [ "$alert_count" -gt 0 ]; then
        log_message "WARNING" "今日共有 $alert_count 个告警"
    else
        log_message "INFO" "今日无告警"
    fi
}

# 错误处理
trap 'log_message "ERROR" "监控脚本执行异常"; exit 1' ERR

# 执行主函数
main "$@" 