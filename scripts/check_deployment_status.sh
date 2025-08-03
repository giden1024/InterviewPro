#!/bin/bash
# 快速检查AWS部署状态

AWS_SERVER="3.138.194.143"
SSH_KEY="~/.ssh/aws-myy-rsa.pem"

echo "🔍 检查AWS服务器部署状态..."

ssh -i "$SSH_KEY" "ec2-user@$AWS_SERVER" << 'EOF'
    echo "=== 服务状态 ==="
    cd /home/ec2-user/InterviewPro
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "=== 后端服务日志 (最近20行) ==="
    docker-compose -f docker-compose.prod.yml logs --tail=20 backend
    
    echo ""
    echo "=== 检查OpenCV错误 ==="
    recent_logs=$(docker-compose -f docker-compose.prod.yml logs --tail=50 backend 2>&1)
    if echo "$recent_logs" | grep -q "libGL.so.1"; then
        echo "❌ 仍然存在OpenCV libGL错误"
        echo "$recent_logs" | grep -A3 -B3 "libGL"
    elif echo "$recent_logs" | grep -q "Worker exiting"; then
        echo "❌ 检测到Worker退出"
        echo "$recent_logs" | grep -A3 -B3 "Worker"
    elif echo "$recent_logs" | grep -q "Successfully"; then
        echo "✅ 服务启动成功"
    else
        echo "⚠️  状态不明确，请查看日志"
    fi
    
    echo ""
    echo "=== 端口监听状态 ==="
    netstat -tlnp 2>/dev/null | grep :5001 || echo "端口5001未监听"
    
    echo ""
    echo "=== 系统资源 ==="
    echo "内存: $(free -h | grep Mem)"
    echo "磁盘: $(df -h / | tail -1)"
EOF

echo ""
echo "🌐 测试网站访问..."
if curl -f -m 10 https://offerott.com >/dev/null 2>&1; then
    echo "✅ 网站可以访问"
else
    echo "❌ 网站无法访问"
fi 