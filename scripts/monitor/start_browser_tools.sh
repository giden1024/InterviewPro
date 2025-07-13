#!/bin/bash

# Browser-tools MCP服务启动脚本
echo "🚀 启动 Browser-tools MCP 服务..."

# 检查是否已有运行的实例
if pgrep -f "browser-tools" > /dev/null; then
    echo "⚠️  检测到已运行的browser-tools进程，正在终止..."
    pkill -f "browser-tools"
    sleep 2
fi

# 启动browser-tools-server (中间件)
echo "📡 启动browser-tools-server (中间件)..."
npx @agentdeskai/browser-tools-server@1.2.0 &
SERVER_PID=$!

# 等待服务器启动
sleep 3

# 检查服务器是否启动成功
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ browser-tools-server 启动成功 (PID: $SERVER_PID)"
else
    echo "❌ browser-tools-server 启动失败"
    exit 1
fi

# 显示服务状态
echo ""
echo "📊 当前运行的browser-tools进程:"
ps aux | grep browser-tools | grep -v grep

echo ""
echo "🎉 Browser-tools MCP服务已启动！"
echo ""
echo "📋 下一步操作:"
echo "1. 确保已安装Chrome扩展"
echo "2. 重启Cursor以加载MCP配置"
echo "3. 在Cursor中测试browser-tools工具"
echo ""
echo "⏹️  要停止服务，运行: pkill -f browser-tools" 