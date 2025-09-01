#!/bin/bash

echo "🚀 验证AWS部署更新 - 后端错误信息同步检查"
echo "=========================================="

# 等待部署完成
echo "⏳ 等待GitHub Actions部署完成..."
sleep 30

# 测试用户不存在的情况
echo ""
echo "🔍 测试1: 用户不存在错误信息"
echo "预期: 英文错误信息"
RESPONSE1=$(curl -s -X POST https://offerott.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"nonexistent@test.com","password":"wrongpass"}' | jq -r '.error.message')

echo "实际返回: $RESPONSE1"

if [[ "$RESPONSE1" == *"User does not exist"* ]]; then
    echo "✅ 用户不存在错误信息已更新为英文版本"
else
    echo "❌ 用户不存在错误信息仍为旧版本: $RESPONSE1"
fi

echo ""
echo "🔍 测试2: 密码错误信息"
echo "预期: 英文错误信息"

# 创建测试用户（如果不存在）
curl -s -X POST https://offerott.com/api/v1/dev/create-test-user > /dev/null 2>&1

RESPONSE2=$(curl -s -X POST https://offerott.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrongpass"}' | jq -r '.error.message')

echo "实际返回: $RESPONSE2"

if [[ "$RESPONSE2" == *"Incorrect password"* ]]; then
    echo "✅ 密码错误信息已更新为英文版本"
else
    echo "❌ 密码错误信息仍为旧版本: $RESPONSE2"
fi

echo ""
echo "🔍 测试3: 健康检查"
HEALTH_STATUS=$(curl -s https://offerott.com/health | jq -r '.status')
echo "健康状态: $HEALTH_STATUS"

echo ""
echo "📊 部署更新验证总结"
echo "==================="

if [[ "$RESPONSE1" == *"User does not exist"* ]] && [[ "$RESPONSE2" == *"Incorrect password"* ]]; then
    echo "🎉 AWS服务器后端代码已成功更新为最新版本！"
    echo "🔧 错误信息已从中文改为英文版本"
    echo "📱 前端现在应该能正确显示错误信息了"
else
    echo "⚠️  部署可能还在进行中，或需要手动检查"
    echo "🔄 建议等待5-10分钟后重新测试"
fi

echo ""
echo "🌐 测试地址: https://offerott.com/login"
echo "📝 如需进一步调试，请查看browser tools MCP输出" 