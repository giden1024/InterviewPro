#!/bin/bash

# 启动后端服务脚本 - 使用完整版本

echo "🚀 启动InterviewPro后端服务..."

# 检查是否在正确的目录
if [ ! -f "backend/run_complete.py" ]; then
    echo "❌ 错误：未找到backend/run_complete.py文件"
    echo "请确保在项目根目录运行此脚本"
    exit 1
fi

# 进入backend目录
cd backend

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 错误：未找到虚拟环境目录 venv"
    echo "请先创建虚拟环境：python -m venv venv"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
echo "📋 检查依赖..."
if ! python -c "import flask" 2>/dev/null; then
    echo "⚠️  正在安装依赖..."
    pip install -r requirements.txt
fi

# 设置环境变量
export FLASK_APP=run_complete.py
export FLASK_ENV=development

echo "🌐 启动后端服务 (使用run_complete.py)..."
echo "📍 访问地址: http://localhost:5001"
echo "🔧 API文档: http://localhost:5001/api/v1/"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=================================================="

# 启动服务
python run_complete.py 