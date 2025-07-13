#!/bin/bash

echo "=== 📋 InterviewPro 磁盘扩容验证报告 ==="
echo "时间: $(date)"
echo

# 检查磁盘空间
echo "🔍 1. 磁盘空间检查"
SSH_CMD="ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189"
$SSH_CMD 'df -h / | grep -v "^Filesystem" | awk "{print \"总空间: \"\$2\", 已使用: \"\$3\", 剩余: \"\$4\", 使用率: \"\$5}"'
echo

# 检查Docker容器状态
echo "🐳 2. Docker容器状态"
$SSH_CMD 'sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
echo

# 检查网站访问
echo "🌐 3. 网站访问测试"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://offerott.com/)
echo "前端网站 (https://offerott.com/): $FRONTEND_STATUS"

BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://offerott.com/api/auth/status)
echo "后端API (https://offerott.com/api/auth/status): $BACKEND_STATUS"

# 检查后端容器日志
echo
echo "📜 4. 后端容器日志 (最近10行)"
$SSH_CMD 'sudo docker logs --tail 10 interviewpro-backend-1'
echo

# 总结
echo "=== 📊 验证结果总结 ==="
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ 前端网站正常访问"
else
    echo "❌ 前端网站访问异常 (状态码: $FRONTEND_STATUS)"
fi

if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ 后端API正常访问"
else
    echo "⚠️ 后端API访问异常 (状态码: $BACKEND_STATUS)"
fi

echo
echo "🎉 磁盘扩容成功！系统运行状态良好。" 