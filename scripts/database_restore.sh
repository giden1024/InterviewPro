#!/bin/bash

# InterviewPro MySQL Database Restore Script
# 功能：从备份文件恢复MySQL数据库

set -e  # 遇到错误时停止脚本

# 配置变量
BACKUP_DIR="/home/ec2-user/backups/mysql"
DB_NAME="interviewpro"
DB_USER="user"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="3306"

# 日志配置
LOG_FILE="/home/ec2-user/logs/restore.log"
DATE=$(date '+%Y-%m-%d_%H-%M-%S')

# 显示帮助信息
show_help() {
    echo "数据库恢复脚本使用说明:"
    echo ""
    echo "用法: $0 [选项] <备份文件>"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示此帮助信息"
    echo "  -l, --list          列出所有可用的备份文件"
    echo "  -f, --force         强制恢复（不提示确认）"
    echo "  --dry-run           测试运行（不实际执行恢复）"
    echo ""
    echo "示例:"
    echo "  $0 interviewpro_backup_2025-07-13_08-00-00.sql.gz"
    echo "  $0 -l                                              # 列出备份文件"
    echo "  $0 -f backup.sql.gz                               # 强制恢复"
    echo ""
}

# 列出可用的备份文件
list_backups() {
    echo "可用的备份文件:"
    echo "===========================================" 
    
    if [ -d "$BACKUP_DIR" ]; then
        BACKUPS=$(find "$BACKUP_DIR" -name "interviewpro_backup_*.sql.gz" -type f | sort -r)
        
        if [ -n "$BACKUPS" ]; then
            echo "$BACKUPS" | while read -r backup; do
                BASENAME=$(basename "$backup")
                SIZE=$(ls -lh "$backup" | awk '{print $5}')
                MTIME=$(stat -c %y "$backup" | cut -d'.' -f1)
                echo "$BASENAME (大小: $SIZE, 时间: $MTIME)"
            done
        else
            echo "没有找到备份文件"
        fi
    else
        echo "备份目录不存在: $BACKUP_DIR"
    fi
    echo "==========================================="
}

# 检查备份文件
check_backup_file() {
    local backup_file=$1
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 检查备份文件: $backup_file" | tee -a "$LOG_FILE"
    
    # 检查文件是否存在
    if [ ! -f "$backup_file" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：备份文件不存在: $backup_file" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 检查文件是否为空
    if [ ! -s "$backup_file" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：备份文件为空: $backup_file" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 检查 gzip 文件完整性
    if [[ "$backup_file" == *.gz ]]; then
        if ! gzip -t "$backup_file"; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：备份文件损坏: $backup_file" | tee -a "$LOG_FILE"
            exit 1
        fi
    fi
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份文件检查通过" | tee -a "$LOG_FILE"
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

# 备份当前数据库
backup_current_database() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份当前数据库..." | tee -a "$LOG_FILE"
    
    local current_backup="${BACKUP_DIR}/current_backup_before_restore_${DATE}.sql.gz"
    
    if docker exec interviewpro-mysql mysqldump \
        -h "$DB_HOST" \
        -P "$DB_PORT" \
        -u "$DB_USER" \
        -p"$DB_PASSWORD" \
        --single-transaction \
        --routines \
        --triggers \
        "$DB_NAME" | gzip > "$current_backup"; then
        
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 当前数据库已备份到: $current_backup" | tee -a "$LOG_FILE"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 警告：当前数据库备份失败" | tee -a "$LOG_FILE"
    fi
}

# 执行数据库恢复
perform_restore() {
    local backup_file=$1
    local dry_run=$2
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始恢复数据库..." | tee -a "$LOG_FILE"
    
    if [ "$dry_run" = "true" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - [测试模式] 将要执行的恢复操作:" | tee -a "$LOG_FILE"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - [测试模式] 数据库: $DB_NAME" | tee -a "$LOG_FILE"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - [测试模式] 备份文件: $backup_file" | tee -a "$LOG_FILE"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - [测试模式] 测试运行完成，未实际执行恢复" | tee -a "$LOG_FILE"
        return 0
    fi
    
    # 删除现有数据库并重新创建
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 重新创建数据库..." | tee -a "$LOG_FILE"
    docker exec interviewpro-mysql mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    
    # 恢复数据
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 从备份文件恢复数据..." | tee -a "$LOG_FILE"
    
    if [[ "$backup_file" == *.gz ]]; then
        # 处理压缩文件
        if gunzip -c "$backup_file" | docker exec -i interviewpro-mysql mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME"; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 数据库恢复成功" | tee -a "$LOG_FILE"
        else
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：数据库恢复失败" | tee -a "$LOG_FILE"
            exit 1
        fi
    else
        # 处理未压缩文件
        if docker exec -i interviewpro-mysql mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$backup_file"; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 数据库恢复成功" | tee -a "$LOG_FILE"
        else
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 错误：数据库恢复失败" | tee -a "$LOG_FILE"
            exit 1
        fi
    fi
}

# 验证恢复结果
verify_restore() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 验证恢复结果..." | tee -a "$LOG_FILE"
    
    # 检查表是否存在
    TABLES=$(docker exec interviewpro-mysql mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES;" | tail -n +2)
    
    if [ -n "$TABLES" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 数据库表验证成功，发现以下表:" | tee -a "$LOG_FILE"
        echo "$TABLES" | while read -r table; do
            echo "$(date '+%Y-%m-%d %H:%M:%S') -   表: $table" | tee -a "$LOG_FILE"
        done
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 警告：没有发现任何数据库表" | tee -a "$LOG_FILE"
    fi
    
    # 检查用户数据
    USER_COUNT=$(docker exec interviewpro-mysql mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT COUNT(*) FROM users;" 2>/dev/null | tail -n +2 || echo "0")
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 用户数据验证: 发现 $USER_COUNT 个用户记录" | tee -a "$LOG_FILE"
}

# 主执行函数
main() {
    local backup_file=""
    local force_restore=false
    local dry_run=false
    local list_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list)
                list_only=true
                shift
                ;;
            -f|--force)
                force_restore=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                if [ -z "$backup_file" ]; then
                    backup_file=$1
                else
                    echo "错误：多余的参数 $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 如果只是列出备份文件
    if [ "$list_only" = true ]; then
        list_backups
        exit 0
    fi
    
    # 检查备份文件参数
    if [ -z "$backup_file" ]; then
        echo "错误：请指定备份文件"
        show_help
        exit 1
    fi
    
    # 如果备份文件不包含路径，假设在备份目录中
    if [[ "$backup_file" != */* ]]; then
        backup_file="$BACKUP_DIR/$backup_file"
    fi
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ===== 开始数据库恢复任务 =====" | tee -a "$LOG_FILE"
    
    check_backup_file "$backup_file"
    check_database_connection
    
    # 确认恢复操作
    if [ "$force_restore" = false ] && [ "$dry_run" = false ]; then
        echo ""
        echo "警告：此操作将完全替换当前数据库！"
        echo "数据库: $DB_NAME"
        echo "备份文件: $backup_file"
        echo ""
        read -p "确认继续吗？(输入 'yes' 继续): " confirm
        
        if [ "$confirm" != "yes" ]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 用户取消恢复操作" | tee -a "$LOG_FILE"
            exit 0
        fi
    fi
    
    # 备份当前数据库
    if [ "$dry_run" = false ]; then
        backup_current_database
    fi
    
    # 执行恢复
    perform_restore "$backup_file" "$dry_run"
    
    # 验证恢复结果
    if [ "$dry_run" = false ]; then
        verify_restore
    fi
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ===== 数据库恢复任务完成 =====" | tee -a "$LOG_FILE"
}

# 错误处理
trap 'echo "$(date) - 错误：恢复过程中发生异常" | tee -a "$LOG_FILE"; exit 1' ERR

# 执行主函数
main "$@" 