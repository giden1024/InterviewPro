#!/bin/bash

# InterviewPro MySQL Database Backup Script
# 功能：定期备份MySQL数据库，保留指定天数的备份，自动清理过期备份

set -e  # 遇到错误时停止脚本

# 配置变量
BACKUP_DIR="/home/ec2-user/backups/mysql"
DB_NAME="interviewpro"
DB_USER="user"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="3306"
RETENTION_DAYS=7  # 保留7天的备份

# 日志配置
LOG_FILE="/home/ec2-user/logs/backup.log"
DATE=$(date '+%Y-%m-%d_%H-%M-%S')
BACKUP_FILE="${BACKUP_DIR}/interviewpro_backup_${DATE}.sql"

# 创建必要的目录
create_directories() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 创建备份目录..." | tee -a "$LOG_FILE"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
}

# 检查磁盘空间
check_disk_space() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 检查磁盘空间..." | tee -a "$LOG_FILE"
    
    # 获取可用空间 (KB)
    AVAILABLE_SPACE=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    REQUIRED_SPACE=1048576  # 1GB in KB
    
    if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：磁盘空间不足。可用: ${AVAILABLE_SPACE}KB，需要: ${REQUIRED_SPACE}KB" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 磁盘空间检查通过。可用: ${AVAILABLE_SPACE}KB" | tee -a "$LOG_FILE"
}

# 检查数据库连接
check_database_connection() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 检查数据库连接..." | tee -a "$LOG_FILE"
    
    if ! docker exec interviewpro-mysql mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" > /dev/null 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：无法连接到数据库" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 数据库连接成功" | tee -a "$LOG_FILE"
}

# 执行数据库备份
perform_backup() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始备份数据库 $DB_NAME..." | tee -a "$LOG_FILE"
    
    # 使用 mysqldump 备份数据库
    if docker exec interviewpro-mysql mysqldump \
        -h "$DB_HOST" \
        -P "$DB_PORT" \
        -u "$DB_USER" \
        -p"$DB_PASSWORD" \
        --single-transaction \
        --routines \
        --triggers \
        --add-drop-table \
        --complete-insert \
        "$DB_NAME" > "$BACKUP_FILE"; then
        
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 数据库备份成功: $BACKUP_FILE" | tee -a "$LOG_FILE"
        
        # 压缩备份文件
        gzip "$BACKUP_FILE"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份文件已压缩: ${BACKUP_FILE}.gz" | tee -a "$LOG_FILE"
        
        # 获取备份文件大小
        BACKUP_SIZE=$(ls -lh "${BACKUP_FILE}.gz" | awk '{print $5}')
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份文件大小: $BACKUP_SIZE" | tee -a "$LOG_FILE"
        
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：数据库备份失败" | tee -a "$LOG_FILE"
        exit 1
    fi
}

# 清理过期备份
cleanup_old_backups() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 清理 $RETENTION_DAYS 天前的备份文件..." | tee -a "$LOG_FILE"
    
    # 查找并删除过期备份
    OLD_BACKUPS=$(find "$BACKUP_DIR" -name "interviewpro_backup_*.sql.gz" -mtime +$RETENTION_DAYS)
    
    if [ -n "$OLD_BACKUPS" ]; then
        echo "$OLD_BACKUPS" | while read -r file; do
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 删除过期备份: $(basename "$file")" | tee -a "$LOG_FILE"
            rm -f "$file"
        done
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 没有找到过期的备份文件" | tee -a "$LOG_FILE"
    fi
}

# 备份验证
verify_backup() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 验证备份文件..." | tee -a "$LOG_FILE"
    
    BACKUP_FILE_GZ="${BACKUP_FILE}.gz"
    
    # 检查文件是否存在且不为空
    if [ -s "$BACKUP_FILE_GZ" ]; then
        # 测试 gzip 文件完整性
        if gzip -t "$BACKUP_FILE_GZ"; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份文件验证成功" | tee -a "$LOG_FILE"
        else
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：备份文件损坏" | tee -a "$LOG_FILE"
            exit 1
        fi
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：备份文件为空或不存在" | tee -a "$LOG_FILE"
        exit 1
    fi
}

# 发送通知（可选）
send_notification() {
    local status=$1
    local message=$2
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 通知: $message" | tee -a "$LOG_FILE"
    
    # 这里可以添加邮件或其他通知方式
    # 例如：echo "$message" | mail -s "数据库备份$status" admin@example.com
}

# 显示备份统计
show_backup_stats() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份统计:" | tee -a "$LOG_FILE"
    
    TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "interviewpro_backup_*.sql.gz" | wc -l)
    TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | awk '{print $1}')
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 总备份数量: $TOTAL_BACKUPS" | tee -a "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 总备份大小: $TOTAL_SIZE" | tee -a "$LOG_FILE"
}

# 主执行函数
main() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ===== 开始数据库备份任务 =====" | tee -a "$LOG_FILE"
    
    create_directories
    check_disk_space
    check_database_connection
    perform_backup
    verify_backup
    cleanup_old_backups
    show_backup_stats
    
    send_notification "成功" "数据库备份完成: ${BACKUP_FILE}.gz"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ===== 数据库备份任务完成 =====" | tee -a "$LOG_FILE"
}

# 错误处理
trap 'echo "$(date) - 错误：备份过程中发生异常" | tee -a "$LOG_FILE"; send_notification "失败" "数据库备份失败"; exit 1' ERR

# 执行主函数
main "$@" 