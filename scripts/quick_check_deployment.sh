#!/bin/bash

echo "⚡ AWS部署状态快速检查"
echo "====================="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查登录API错误信息
echo "🔍 检查错误信息语言..."
ERROR_MSG=$(curl -s -X POST https://offerott.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"nonexistent@test.com","password":"wrongpass"}' | \
  jq -r '.error.message' 2>/dev/null)

echo "返回的错误信息: $ERROR_MSG"

if [[ "$ERROR_MSG" == *"User does not exist"* ]]; then
    echo "✅ 部署成功！代码已更新为英文版本"
    echo "🎉 前端现在应该能正确显示错误信息"
    exit 0
elif [[ "$ERROR_MSG" == *"用户不存在"* ]]; then
    echo "❌ 部署未完成，仍为中文版本"
    echo "⏳ 建议继续等待或手动部署"
    exit 1
else
    echo "⚠️  未知响应格式: $ERROR_MSG"
    echo "🔧 可能需要检查API连接状态"
    exit 2
fi 