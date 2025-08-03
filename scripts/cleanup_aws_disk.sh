#!/bin/bash
# AWS服务器磁盘清理脚本

AWS_SERVER="3.138.194.143"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"

echo "🧹 开始清理AWS服务器磁盘空间..."

ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    echo "=== 清理前磁盘状态 ==="
    df -h
    
    echo ""
    echo "=== 1. 清理Docker资源 ==="
    cd /home/ec2-user/InterviewPro
    
    # 停止所有容器
    docker-compose -f docker-compose.prod.yml down
    
    # 清理所有Docker资源
    echo "清理Docker镜像..."
    docker system prune -af
    
    echo "清理Docker卷..."
    docker volume prune -f
    
    echo "清理Docker网络..."
    docker network prune -f
    
    echo "清理构建缓存..."
    docker builder prune -af
    
    echo ""
    echo "=== 2. 清理系统缓存 ==="
    # 清理包管理器缓存
    sudo dnf clean all
    
    # 清理临时文件
    sudo rm -rf /tmp/*
    sudo rm -rf /var/tmp/*
    
    # 清理日志文件
    sudo journalctl --vacuum-time=7d
    sudo find /var/log -name "*.log" -type f -mtime +7 -delete
    
    echo ""
    echo "=== 3. 清理项目文件 ==="
    # 清理Git缓存
    git gc --aggressive --prune=now
    
    # 清理Python缓存
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete
    
    # 清理node_modules如果存在
    find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # 清理备份文件
    find . -name "*.tar.gz" -size +10M -mtime +1 -delete 2>/dev/null || true
    
    echo ""
    echo "=== 4. 清理后磁盘状态 ==="
    df -h
    
    echo ""
    echo "=== 5. 检查最大文件 ==="
    echo "最大的10个文件/目录:"
    du -ah / 2>/dev/null | sort -rh | head -10
    
    echo ""
    echo "=== 6. 检查可用空间 ==="
    available_space=$(df / | awk 'NR==2 {print $4}')
    available_gb=$((available_space / 1024 / 1024))
    
    if [ $available_gb -lt 2 ]; then
        echo "❌ 可用空间不足 (${available_gb}GB)，建议扩容"
        exit 1
    else
        echo "✅ 可用空间充足 (${available_gb}GB)"
    fi
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 磁盘清理完成!"
    echo "现在可以重新尝试部署"
else
    echo "❌ 磁盘清理失败或空间仍然不足"
    echo "建议手动扩容AWS EBS卷"
    exit 1
fi 