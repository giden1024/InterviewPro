#!/bin/bash

# Google OAuth 快速修复脚本
# 用于修复 "invalid_client" 错误

echo "🔐 Google OAuth 修复脚本"
echo "=========================="

# 检查是否在正确的目录
if [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "📁 创建前端环境变量文件..."

# 创建 .env.local 文件
cat > frontend/.env.local << 'EOF'
# Google OAuth 配置
# 请将下面的占位符替换为真实的 Google OAuth Client ID
VITE_GOOGLE_CLIENT_ID=your-google-client-id-here

# Facebook OAuth 配置 (可选)
VITE_FACEBOOK_APP_ID=your-facebook-app-id-here

# OAuth 回调地址
VITE_OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback

# API 基础地址
VITE_API_BASE_URL=http://localhost:5001/api/v1
EOF

echo "✅ 已创建 frontend/.env.local 文件"

echo ""
echo "🔧 下一步操作:"
echo "1. 访问 Google Cloud Console: https://console.cloud.google.com/"
echo "2. 创建 OAuth 客户端ID"
echo "3. 编辑 frontend/.env.local 文件，替换 'your-google-client-id-here' 为真实的客户端ID"
echo ""
echo "💡 临时解决方案 - 禁用 Google OAuth:"
echo "如果暂时不需要 Google 登录，可以运行: ./fix_google_oauth.sh --disable"

# 检查是否需要禁用 Google OAuth
if [ "$1" = "--disable" ]; then
    echo ""
    echo "🚫 禁用 Google OAuth 登录按钮..."
    
    # 备份原文件
    cp frontend/src/components/LoginPage/LoginPage.tsx frontend/src/components/LoginPage/LoginPage.tsx.backup
    
    # 注释掉 Google 登录按钮（这里只是示例，实际需要更精确的替换）
    echo "⚠️  请手动编辑 frontend/src/components/LoginPage/LoginPage.tsx"
    echo "   注释掉 Google 登录相关的按钮代码"
    echo ""
    echo "📄 已备份原文件到: frontend/src/components/LoginPage/LoginPage.tsx.backup"
fi

echo ""
echo "🔄 修复完成后，请重启前端服务:"
echo "   cd frontend && npm run dev"
echo ""
echo "✅ 修复完成!" 