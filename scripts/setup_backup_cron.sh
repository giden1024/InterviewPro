#!/bin/bash

# InterviewPro Database Backup Cron Setup Script
# 功能：设置数据库备份的定时任务

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/database_backup.sh"

echo "===================================================="
echo "InterviewPro 数据库备份定时任务设置"
echo "===================================================="

# 检查备份脚本是否存在
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "错误：备份脚本不存在: $BACKUP_SCRIPT"
    exit 1
fi

# 确保备份脚本有执行权限
chmod +x "$BACKUP_SCRIPT"

# 显示当前的 crontab
echo "当前的定时任务:"
echo "----------------------------------------------------"
crontab -l 2>/dev/null || echo "没有现有的定时任务"
echo "----------------------------------------------------"

# 检查是否已经存在备份任务
if crontab -l 2>/dev/null | grep -q "database_backup.sh"; then
    echo ""
    echo "检测到已存在的数据库备份定时任务。"
    read -p "是否要覆盖现有设置？(y/N): " overwrite
    
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo "操作已取消。"
        exit 0
    fi
    
    # 移除现有的备份任务
    echo "移除现有的备份定时任务..."
    (crontab -l 2>/dev/null | grep -v "database_backup.sh") | crontab -
fi

echo ""
echo "选择备份频率:"
echo "1) 每天凌晨2点备份 (推荐)"
echo "2) 每12小时备份一次 (2:00 和 14:00)"
echo "3) 每6小时备份一次"
echo "4) 每小时备份一次 (测试用)"
echo "5) 自定义时间"

read -p "请选择 (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="每天凌晨2点"
        ;;
    2)
        CRON_SCHEDULE="0 2,14 * * *"
        DESCRIPTION="每天2:00和14:00"
        ;;
    3)
        CRON_SCHEDULE="0 */6 * * *"
        DESCRIPTION="每6小时"
        ;;
    4)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="每小时"
        ;;
    5)
        echo ""
        echo "自定义cron表达式格式: 分钟 小时 日 月 星期"
        echo "示例: 0 2 * * * (每天凌晨2点)"
        read -p "请输入cron表达式: " CRON_SCHEDULE
        DESCRIPTION="自定义时间"
        ;;
    *)
        echo "无效选择，使用默认设置 (每天凌晨2点)"
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="每天凌晨2点"
        ;;
esac

# 创建新的crontab条目
CRON_ENTRY="$CRON_SCHEDULE $BACKUP_SCRIPT >> /home/ec2-user/logs/backup.log 2>&1"

echo ""
echo "准备添加以下定时任务:"
echo "时间: $DESCRIPTION"
echo "表达式: $CRON_SCHEDULE"
echo ""

read -p "确认添加？(y/N): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "操作已取消。"
    exit 0
fi

# 添加定时任务
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo ""
echo "✅ 定时任务添加成功！" 