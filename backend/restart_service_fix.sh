#!/bin/bash
# 重启后端服务以应用.doc文件解析修复

echo "🔄 重启后端服务以应用.doc文件解析修复..."

# 停止现有服务
echo "⏹️ 停止现有服务..."
pkill -f run_complete.py
sleep 2

# 检查并安装必要依赖
echo "📦 检查依赖..."
pip install opencv-python-headless==4.8.1.78 > /dev/null 2>&1

# 启动服务
echo "🚀 启动后端服务..."
echo "📍 访问地址: http://localhost:5001"
echo "🧪 测试页面: http://localhost:3000/test-resume-parser.html"
echo "按 Ctrl+C 停止服务"
echo "=================================="

python run_complete.py 