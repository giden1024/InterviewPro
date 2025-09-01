#!/bin/bash

# 部署到生产环境并启用正式Creem.io的脚本

echo "🚀 开始部署InterviewPro到生产环境 (启用正式Creem.io)"

# 1. 检查必需的环境变量
echo "📋 检查环境变量..."

required_vars=(
    "CREEM_API_KEY"
    "CREEM_BASIC_PRODUCT_ID" 
    "CREEM_PREMIUM_PRODUCT_ID"
    "DATABASE_URL"
    "FRONTEND_URL"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo "❌ 缺少必需的环境变量:"
    printf '  - %s\n' "${missing_vars[@]}"
    echo ""
    echo "请设置这些环境变量后重新运行脚本"
    echo "或者编辑 production_creem_config.env 文件"
    exit 1
fi

# 2. 备份当前配置
echo "💾 备份当前配置..."
if [[ -f "backend/app/config.py" ]]; then
    cp backend/app/config.py backend/app/config.py.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ 配置已备份"
fi

# 3. 设置生产环境变量
echo "⚙️ 设置生产环境配置..."
export FLASK_ENV=production
export DEBUG=False
export CREEM_TEST_MODE=False

echo "✅ 生产环境配置已设置:"
echo "  - FLASK_ENV: $FLASK_ENV"
echo "  - DEBUG: $DEBUG" 
echo "  - CREEM_TEST_MODE: $CREEM_TEST_MODE"
echo "  - FRONTEND_URL: $FRONTEND_URL"

# 4. 检查Creem.io配置
echo "🔍 验证Creem.io配置..."
if [[ $CREEM_API_KEY == *"test"* ]]; then
    echo "⚠️ 警告: API密钥似乎是测试密钥"
    echo "   请确保使用正式的生产API密钥"
fi

# 5. 构建Docker镜像
echo "🐳 构建Docker镜像..."
if ! docker-compose -f docker-compose.prod.yml build; then
    echo "❌ Docker构建失败"
    exit 1
fi

# 6. 启动服务
echo "🚀 启动生产服务..."
if ! docker-compose -f docker-compose.prod.yml up -d; then
    echo "❌ 服务启动失败"
    exit 1
fi

# 7. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 8. 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 9. 测试回调URL可访问性
if [[ -n "$FRONTEND_URL" ]]; then
    callback_url="${FRONTEND_URL/localhost:3000/}/api/v1/billing/callback"
    echo "🔗 回调URL: $callback_url"
    
    # 测试URL可访问性
    if curl -s -o /dev/null -w "%{http_code}" "$callback_url" | grep -q "200\|400\|404"; then
        echo "✅ 回调URL可访问"
    else
        echo "⚠️ 回调URL可能无法访问，请检查防火墙和域名配置"
    fi
fi

# 10. 显示重要信息
echo ""
echo "🎉 部署完成!"
echo ""
echo "📋 重要信息:"
echo "  - 前端URL: $FRONTEND_URL"
echo "  - 回调URL: ${FRONTEND_URL}/api/v1/billing/callback"
echo "  - Creem测试模式: 已关闭 (使用正式API)"
echo ""
echo "📝 下一步操作:"
echo "  1. 在Creem.io控制台配置webhook URL: ${FRONTEND_URL}/api/v1/billing/callback"
echo "  2. 确保使用正式的产品ID和API密钥"
echo "  3. 测试支付流程"
echo ""
echo "🔧 如需查看日志:"
echo "  docker-compose -f docker-compose.prod.yml logs -f backend"
