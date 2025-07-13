#!/bin/bash

# InterviewPro Performance Optimization and Load Testing Script
# 功能：系统性能优化和负载测试

set -e

# 配置变量
LOG_FILE="/home/ec2-user/logs/performance.log"
REPORT_DIR="/home/ec2-user/reports"
DATE=$(date '+%Y-%m-%d_%H-%M-%S')
BASE_URL="https://offerott.com"

# 记录日志
log_message() {
    local level=$1
    local message=$2
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $message" | tee -a "$LOG_FILE"
}

# 系统优化
optimize_system() {
    log_message "INFO" "开始系统优化..."
    
    # 1. 优化内核参数
    log_message "INFO" "优化内核参数..."
    sudo tee -a /etc/sysctl.conf << 'EOF'
# InterviewPro 性能优化
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
EOF
    
    sudo sysctl -p
    
    # 2. 优化文件描述符限制
    log_message "INFO" "优化文件描述符限制..."
    sudo tee -a /etc/security/limits.conf << 'EOF'
# InterviewPro 性能优化
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF
    
    # 3. 配置Swap优化
    log_message "INFO" "优化Swap设置..."
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
    echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
    
    log_message "INFO" "系统优化完成"
}

# 数据库性能优化
optimize_database() {
    log_message "INFO" "优化数据库性能..."
    
    # 创建数据库优化配置
    cat > /tmp/mysql_optimization.cnf << 'EOF'
[mysqld]
# InterviewPro MySQL 性能优化
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
innodb_log_buffer_size = 16M
innodb_flush_log_at_trx_commit = 2
innodb_file_per_table = 1
innodb_flush_method = O_DIRECT

# 查询缓存
query_cache_size = 64M
query_cache_type = 1
query_cache_limit = 4M

# 连接优化
max_connections = 50
thread_cache_size = 16
table_open_cache = 1024

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
EOF
    
    # 注意：这需要重启数据库容器才能生效
    log_message "INFO" "数据库优化配置已准备，需要重启数据库容器以应用"
    log_message "INFO" "建议在维护窗口执行: docker restart interviewpro-mysql"
}

# Redis性能优化
optimize_redis() {
    log_message "INFO" "优化Redis性能..."
    
    # 检查Redis内存使用
    local redis_memory=$(docker exec ec2-user-redis-1 redis-cli INFO memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    log_message "INFO" "当前Redis内存使用: $redis_memory"
    
    # 设置Redis优化参数
    docker exec ec2-user-redis-1 redis-cli CONFIG SET save "900 1 300 10 60 10000"
    docker exec ec2-user-redis-1 redis-cli CONFIG SET maxmemory-policy allkeys-lru
    docker exec ec2-user-redis-1 redis-cli CONFIG SET tcp-keepalive 60
    
    log_message "INFO" "Redis优化完成"
}

# Nginx性能优化
optimize_nginx() {
    log_message "INFO" "优化Nginx性能..."
    
    # 检查当前Nginx配置
    if docker exec ec2-user-nginx-1 nginx -t 2>/dev/null; then
        log_message "INFO" "当前Nginx配置有效"
    else
        log_message "WARNING" "Nginx配置存在问题"
    fi
    
    # 建议的Nginx优化配置（需要更新配置文件）
    cat > /tmp/nginx_optimization.conf << 'EOF'
# Nginx性能优化建议配置
worker_processes auto;
worker_connections 2048;
worker_rlimit_nofile 65535;

# 启用gzip压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript 
           application/javascript application/json application/xml+rss;

# 缓存设置
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# 限制请求
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
EOF
    
    log_message "INFO" "Nginx优化建议已保存到 /tmp/nginx_optimization.conf"
}

# 基础性能测试
basic_performance_test() {
    log_message "INFO" "开始基础性能测试..."
    
    # 1. 网站响应时间测试
    log_message "INFO" "测试网站响应时间..."
    local response_time=$(curl -o /dev/null -s -w '%{time_total}' "$BASE_URL")
    log_message "INFO" "网站响应时间: ${response_time}s"
    
    # 2. API响应时间测试
    log_message "INFO" "测试API响应时间..."
    local api_response_time=$(curl -o /dev/null -s -w '%{time_total}' "$BASE_URL/api/v1/")
    log_message "INFO" "API响应时间: ${api_response_time}s"
    
    # 3. 数据库连接测试
    log_message "INFO" "测试数据库连接时间..."
    local db_start_time=$(date +%s.%N)
    docker exec interviewpro-mysql mysql -u user -p'password' -e "SELECT 1;" > /dev/null 2>&1
    local db_end_time=$(date +%s.%N)
    local db_response_time=$(echo "$db_end_time - $db_start_time" | bc -l)
    log_message "INFO" "数据库连接时间: ${db_response_time}s"
    
    # 4. 内存和CPU使用率
    local memory_usage=$(free | awk 'NR==2{printf "%.1f", $3/$2*100}')
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    log_message "INFO" "当前资源使用 - CPU: ${cpu_usage}%, 内存: ${memory_usage}%"
}

# 负载测试（简单版）
simple_load_test() {
    log_message "INFO" "开始简单负载测试..."
    
    # 检查是否安装了ab工具
    if ! command -v ab &> /dev/null; then
        log_message "INFO" "安装Apache Bench工具..."
        sudo yum install -y httpd-tools
    fi
    
    # 测试主页
    log_message "INFO" "负载测试主页 (100个请求，并发10)..."
    ab -n 100 -c 10 "$BASE_URL/" > /tmp/ab_homepage.txt 2>&1
    
    local requests_per_second=$(grep "Requests per second" /tmp/ab_homepage.txt | awk '{print $4}')
    local time_per_request=$(grep "Time per request.*mean" /tmp/ab_homepage.txt | head -1 | awk '{print $4}')
    
    log_message "INFO" "主页性能 - 每秒处理: ${requests_per_second} 请求/秒, 平均响应时间: ${time_per_request}ms"
    
    # 测试API接口
    log_message "INFO" "负载测试API接口 (50个请求，并发5)..."
    ab -n 50 -c 5 "$BASE_URL/api/v1/" > /tmp/ab_api.txt 2>&1
    
    local api_requests_per_second=$(grep "Requests per second" /tmp/ab_api.txt | awk '{print $4}')
    local api_time_per_request=$(grep "Time per request.*mean" /tmp/ab_api.txt | head -1 | awk '{print $4}')
    
    log_message "INFO" "API性能 - 每秒处理: ${api_requests_per_second} 请求/秒, 平均响应时间: ${api_time_per_request}ms"
}

# 数据库性能测试
database_performance_test() {
    log_message "INFO" "开始数据库性能测试..."
    
    # 创建测试表和数据
    docker exec interviewpro-mysql mysql -u user -p'password' interviewpro << 'EOF'
CREATE TABLE IF NOT EXISTS performance_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_data VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF
    
    # 插入测试数据
    log_message "INFO" "插入1000条测试数据..."
    local insert_start_time=$(date +%s.%N)
    
    for i in {1..1000}; do
        docker exec interviewpro-mysql mysql -u user -p'password' interviewpro -e "INSERT INTO performance_test (test_data) VALUES ('test_data_$i');" > /dev/null 2>&1
    done
    
    local insert_end_time=$(date +%s.%N)
    local insert_duration=$(echo "$insert_end_time - $insert_start_time" | bc -l)
    log_message "INFO" "数据插入完成，耗时: ${insert_duration}s"
    
    # 查询性能测试
    log_message "INFO" "测试查询性能..."
    local query_start_time=$(date +%s.%N)
    
    for i in {1..100}; do
        docker exec interviewpro-mysql mysql -u user -p'password' interviewpro -e "SELECT * FROM performance_test WHERE id = $((RANDOM % 1000 + 1));" > /dev/null 2>&1
    done
    
    local query_end_time=$(date +%s.%N)
    local query_duration=$(echo "$query_end_time - $query_start_time" | bc -l)
    log_message "INFO" "100次查询完成，耗时: ${query_duration}s"
    
    # 清理测试数据
    docker exec interviewpro-mysql mysql -u user -p'password' interviewpro -e "DROP TABLE performance_test;" > /dev/null 2>&1
    log_message "INFO" "测试数据已清理"
}

# 生成性能报告
generate_performance_report() {
    local report_file="$REPORT_DIR/performance_report_${DATE}.txt"
    
    log_message "INFO" "生成性能报告: $report_file"
    
    mkdir -p "$REPORT_DIR"
    
    cat > "$report_file" << EOF
InterviewPro 性能测试报告
生成时间: $(date '+%Y-%m-%d %H:%M:%S')
======================================================

系统资源状态:
CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
内存使用: $(free -h | awk 'NR==2{printf "使用: %s/%s (%.1f%%)", $3,$2,$3/$2*100}')
磁盘使用: $(df -h / | awk 'NR==2{printf "使用: %s/%s (%s)", $3,$2,$5}')
网络连接: $(ss -tuln | wc -l) 个活动连接

Docker容器状态:
$(docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}')

负载测试结果:
$(cat /tmp/ab_homepage.txt 2>/dev/null | grep -E "Requests per second|Time per request|Transfer rate" | head -3 || echo "负载测试未执行")

API测试结果:
$(cat /tmp/ab_api.txt 2>/dev/null | grep -E "Requests per second|Time per request|Transfer rate" | head -3 || echo "API测试未执行")

性能优化建议:
1. 数据库优化配置已准备，建议在维护窗口重启数据库
2. Nginx优化建议保存在 /tmp/nginx_optimization.conf
3. 系统内核参数已优化
4. 定期监控资源使用情况

======================================================
EOF
    
    log_message "INFO" "性能报告已保存到: $report_file"
}

# 性能监控
monitor_performance() {
    log_message "INFO" "开始性能监控..."
    
    local duration=${1:-60}  # 默认监控60秒
    local interval=5
    local count=$((duration / interval))
    
    log_message "INFO" "将监控 $duration 秒，每 $interval 秒记录一次"
    
    for ((i=1; i<=count; i++)); do
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
        local memory=$(free | awk 'NR==2{printf "%.1f", $3/$2*100}')
        local connections=$(ss -tuln | wc -l)
        
        log_message "MONITOR" "[$i/$count] CPU: ${cpu}%, 内存: ${memory}%, 连接: $connections"
        
        sleep $interval
    done
    
    log_message "INFO" "性能监控完成"
}

# 显示帮助信息
show_help() {
    echo "InterviewPro 性能优化和测试工具"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --optimize          执行系统优化"
    echo "  --test              执行性能测试"
    echo "  --load-test         执行负载测试"
    echo "  --monitor [秒数]    性能监控（默认60秒）"
    echo "  --report            生成性能报告"
    echo "  --all               执行所有操作"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --all                    # 执行完整的优化和测试"
    echo "  $0 --test --report          # 只执行测试并生成报告"
    echo "  $0 --monitor 120            # 监控2分钟"
    echo ""
}

# 主执行函数
main() {
    mkdir -p "$(dirname "$LOG_FILE")" "$REPORT_DIR"
    
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    log_message "INFO" "===== 开始性能优化和测试 ====="
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --optimize)
                optimize_system
                optimize_database
                optimize_redis
                optimize_nginx
                shift
                ;;
            --test)
                basic_performance_test
                database_performance_test
                shift
                ;;
            --load-test)
                simple_load_test
                shift
                ;;
            --monitor)
                local duration=${2:-60}
                monitor_performance "$duration"
                shift 2
                ;;
            --report)
                generate_performance_report
                shift
                ;;
            --all)
                optimize_system
                optimize_database
                optimize_redis
                optimize_nginx
                basic_performance_test
                simple_load_test
                database_performance_test
                generate_performance_report
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_message "INFO" "===== 性能优化和测试完成 ====="
}

# 错误处理
trap 'log_message "ERROR" "脚本执行异常"; exit 1' ERR

# 执行主函数
main "$@" 