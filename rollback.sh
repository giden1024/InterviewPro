#!/bin/bash

# ============================================
# InterviewPro 回滚脚本
# 支持回滚到指定版本或最近的备份
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

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# 显示使用方法
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -l, --list                    列出可用的备份"
    echo "  -r, --rollback [BACKUP_ID]    回滚到指定备份（不指定则回滚到最近备份）"
    echo "  -c, --current                 显示当前部署状态"
    echo "  -h, --help                   显示此帮助信息"
    echo ""
    echo "Examples:"
    echo "  $0 --list                     # 列出所有可用备份"
    echo "  $0 --rollback                 # 回滚到最近的备份"
    echo "  $0 --rollback deploy_20240101_120000  # 回滚到指定备份"
    echo "  $0 --current                  # 显示当前状态"
}

# 检查SSH连接
check_ssh_connection() {
    if [ ! -f "$KEY_FILE" ]; then
        error "SSH密钥文件 $KEY_FILE 不存在"
        exit 1
    fi
    
    if ! ssh -i "$KEY_FILE" -o ConnectTimeout=10 "$REMOTE_USER@$SERVER_IP" "echo 'SSH连接成功'" &>/dev/null; then
        error "SSH连接失败，请检查服务器状态和网络连接"
        exit 1
    fi
}

# 列出可用的备份
list_backups() {
    log "📋 列出可用备份..."
    
    check_ssh_connection
    
    local backups=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd /home/ubuntu
        ls -la | grep '$PROJECT_NAME-backup-' | awk '{print \$9, \$6, \$7, \$8}' | sort -r
    " 2>/dev/null)
    
    if [ -z "$backups" ]; then
        warning "没有找到任何备份"
        return 1
    fi
    
    echo ""
    echo "======================================"
    echo "           可用备份列表"
    echo "======================================"
    printf "%-25s %-15s\n" "备份ID" "创建时间"
    echo "--------------------------------------"
    
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            local backup_name=$(echo "$line" | awk '{print $1}')
            local backup_time=$(echo "$line" | awk '{print $2, $3, $4}')
            local backup_id=${backup_name#"$PROJECT_NAME-backup-"}
            printf "%-25s %-15s\n" "$backup_id" "$backup_time"
        fi
    done <<< "$backups"
    
    echo "======================================"
    echo ""
    success "找到 $(echo "$backups" | wc -l) 个备份"
}

# 显示当前部署状态
show_current_status() {
    log "📊 显示当前部署状态..."
    
    check_ssh_connection
    
    echo ""
    echo "======================================"
    echo "          当前部署状态"
    echo "======================================"
    
    # 检查项目目录
    local project_exists=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        [ -d '$REMOTE_PATH' ] && echo 'exists' || echo 'missing'
    " 2>/dev/null)
    
    if [ "$project_exists" == "exists" ]; then
        echo "项目目录: ✅ 存在"
        
        # 获取Git信息
        local git_info=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
            cd '$REMOTE_PATH'
            if [ -d '.git' ]; then
                echo 'Branch: '$(git branch --show-current 2>/dev/null || echo 'Unknown')
                echo 'Commit: '$(git log -1 --format='%h %s' 2>/dev/null || echo 'Unknown')
                echo 'Date: '$(git log -1 --format='%cd' --date=short 2>/dev/null || echo 'Unknown')
            else
                echo 'Git: Not a git repository'
            fi
        " 2>/dev/null)
        
        echo "$git_info" | sed 's/^/  /'
        
        # 检查Docker容器状态
        local containers=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
            cd '$REMOTE_PATH'
            docker-compose -f docker-compose.prod.yml ps --format 'table' 2>/dev/null || echo 'No containers'
        " 2>/dev/null)
        
        echo ""
        echo "Docker 容器状态:"
        echo "$containers" | sed 's/^/  /'
        
        # 检查服务健康状态
        echo ""
        echo "服务健康检查:"
        if curl -s -f "https://$SERVER_IP/api/v1/health" &>/dev/null; then
            echo "  API健康检查: ✅ 正常"
        else
            echo "  API健康检查: ❌ 失败"
        fi
        
        if curl -s -f "https://$SERVER_IP" &>/dev/null; then
            echo "  前端访问: ✅ 正常"
        else
            echo "  前端访问: ❌ 失败"
        fi
        
    else
        echo "项目目录: ❌ 不存在"
    fi
    
    echo "======================================"
}

# 执行回滚
perform_rollback() {
    local backup_id="$1"
    
    log "🔄 开始回滚操作..."
    
    check_ssh_connection
    
    # 如果没有指定备份ID，使用最近的备份
    if [ -z "$backup_id" ]; then
        log "查找最近的备份..."
        backup_id=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
            cd /home/ubuntu
            ls -t | grep '$PROJECT_NAME-backup-' | head -1 | sed 's/$PROJECT_NAME-backup-//'
        " 2>/dev/null)
        
        if [ -z "$backup_id" ]; then
            error "没有找到可用的备份"
            exit 1
        fi
        
        log "找到最近的备份: $backup_id"
    fi
    
    local backup_dir="$PROJECT_NAME-backup-$backup_id"
    
    # 验证备份存在
    local backup_exists=$(ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        [ -d '/home/ubuntu/$backup_dir' ] && echo 'exists' || echo 'missing'
    " 2>/dev/null)
    
    if [ "$backup_exists" != "exists" ]; then
        error "备份不存在: $backup_dir"
        exit 1
    fi
    
    # 确认回滚操作
    warning "即将回滚到备份: $backup_id"
    read -p "确认要执行回滚吗？这将替换当前的部署 (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "回滚操作已取消"
        exit 0
    fi
    
    # 执行回滚
    log "执行回滚操作..."
    
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" << EOF
        set -e
        
        echo "🛑 停止当前服务..."
        if [ -d '$REMOTE_PATH' ]; then
            cd '$REMOTE_PATH'
            docker-compose -f docker-compose.prod.yml down &>/dev/null || true
        fi
        
        echo "💾 创建当前状态的紧急备份..."
        if [ -d '$REMOTE_PATH' ]; then
            emergency_backup="$PROJECT_NAME-emergency-\$(date +%Y%m%d_%H%M%S)"
            cp -r '$REMOTE_PATH' "/home/ubuntu/\$emergency_backup"
            echo "✅ 紧急备份已创建: \$emergency_backup"
        fi
        
        echo "🔄 执行回滚..."
        cd /home/ubuntu
        rm -rf '$REMOTE_PATH'
        cp -r '$backup_dir' '$PROJECT_NAME'
        
        echo "🚀 启动服务..."
        cd '$REMOTE_PATH'
        docker-compose -f docker-compose.prod.yml up -d &>/dev/null || true
        
        echo "⏳ 等待服务启动..."
        sleep 30
        
        echo "✅ 回滚完成"
EOF
    
    success "回滚操作完成"
    
    # 验证回滚结果
    log "验证回滚结果..."
    sleep 10
    
    local health_check_attempts=5
    local attempt=1
    
    while [ $attempt -le $health_check_attempts ]; do
        log "健康检查 $attempt/$health_check_attempts..."
        
        if curl -s -f "https://$SERVER_IP/api/v1/health" &>/dev/null; then
            success "回滚成功！服务正常运行"
            show_current_status
            return 0
        fi
        
        if [ $attempt -eq $health_check_attempts ]; then
            error "回滚后健康检查失败"
            warning "请手动检查服务状态"
            return 1
        fi
        
        sleep 15
        ((attempt++))
    done
}

# 清理旧备份
cleanup_old_backups() {
    log "🧹 清理旧备份..."
    
    check_ssh_connection
    
    # 保留最近的5个备份
    local keep_count=5
    
    ssh -i "$KEY_FILE" "$REMOTE_USER@$SERVER_IP" "
        cd /home/ubuntu
        
        # 获取所有备份，按时间排序
        backups=\$(ls -t | grep '$PROJECT_NAME-backup-' | tail -n +\$((keep_count + 1)))
        
        if [ -n \"\$backups\" ]; then
            echo \"清理以下旧备份:\"
            echo \"\$backups\" | sed 's/^/  /'
            echo \"\$backups\" | xargs rm -rf
            echo \"✅ 旧备份清理完成\"
        else
            echo \"没有需要清理的旧备份\"
        fi
    "
    
    success "备份清理完成"
}

# 主函数
main() {
    local action=""
    local backup_id=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -l|--list)
                action="list"
                shift
                ;;
            -r|--rollback)
                action="rollback"
                if [[ $2 && ! $2 =~ ^- ]]; then
                    backup_id="$2"
                    shift
                fi
                shift
                ;;
            -c|--current)
                action="current"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            --cleanup)
                action="cleanup"
                shift
                ;;
            *)
                error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定操作，显示使用方法
    if [ -z "$action" ]; then
        show_usage
        exit 1
    fi
    
    # 执行相应操作
    case $action in
        list)
            list_backups
            ;;
        rollback)
            perform_rollback "$backup_id"
            ;;
        current)
            show_current_status
            ;;
        cleanup)
            cleanup_old_backups
            ;;
        *)
            error "无效操作: $action"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 