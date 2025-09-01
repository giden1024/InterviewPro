#!/bin/bash

# 简历解析测试环境启动脚本
echo "🚀 启动简历解析测试环境..."

# 检查是否在项目根目录
if [ ! -f "backend/run_complete.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用"
        return 1
    fi
    return 0
}

# 启动后端服务
start_backend() {
    echo "📦 启动后端服务..."
    cd backend
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo "❌ 后端虚拟环境不存在，请先创建虚拟环境"
        exit 1
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查依赖
    if ! python -c "import flask" 2>/dev/null; then
        echo "❌ 后端依赖未安装，请运行 pip install -r requirements.txt"
        exit 1
    fi
    
    # 启动后端
    echo "🔧 后端服务启动中..."
    python run_complete.py &
    BACKEND_PID=$!
    
    # 等待后端启动
    sleep 3
    
    # 检查后端是否启动成功
    if curl -s http://localhost:5001/health >/dev/null 2>&1; then
        echo "✅ 后端服务启动成功 (PID: $BACKEND_PID)"
        echo "📍 后端地址: http://localhost:5001"
        echo "🔧 API文档: http://localhost:5001/api/v1/"
    else
        echo "❌ 后端服务启动失败"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    cd ..
}

# 启动前端服务
start_frontend() {
    echo "🌐 启动前端服务..."
    cd frontend
    
    # 检查Node.js
    if ! command -v node >/dev/null 2>&1; then
        echo "❌ Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    # 检查依赖
    if [ ! -d "node_modules" ]; then
        echo "📦 安装前端依赖..."
        npm install
    fi
    
    # 启动前端
    echo "🎨 前端服务启动中..."
    npm run dev &
    FRONTEND_PID=$!
    
    # 等待前端启动
    sleep 5
    
    # 检查前端是否启动成功
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ 前端服务启动成功 (PID: $FRONTEND_PID)"
        echo "📍 前端地址: http://localhost:3000"
        echo "🧪 测试页面: http://localhost:3000/test-resume-parser.html"
    else
        echo "❌ 前端服务启动失败"
        kill $FRONTEND_PID 2>/dev/null
        exit 1
    fi
    
    cd ..
}

# 显示使用说明
show_usage() {
    echo ""
    echo "======================================================"
    echo "🎯 简历解析测试环境已启动"
    echo "======================================================"
    echo ""
    echo "📋 服务地址:"
    echo "  - 后端服务: http://localhost:5001"
    echo "  - 前端服务: http://localhost:3000"
    echo "  - 测试页面: http://localhost:3000/test-resume-parser.html"
    echo ""
    echo "🔧 测试步骤:"
    echo "  1. 打开测试页面"
    echo "  2. 注册/登录用户账号"
    echo "  3. 上传简历文件 (PDF/DOCX/DOC/TXT)"
    echo "  4. 查看解析结果"
    echo ""
    echo "💡 测试建议:"
    echo "  - 使用不同格式的简历文件"
    echo "  - 测试各种解析场景"
    echo "  - 检查解析结果的准确性"
    echo ""
    echo "📁 支持的文件格式:"
    echo "  - PDF: ✅ 支持"
    echo "  - DOCX: ✅ 支持"
    echo "  - DOC: ⚠️ 有限支持 (会提示转换)"
    echo "  - TXT: ✅ 支持"
    echo ""
    echo "🛑 停止服务:"
    echo "  - 按 Ctrl+C 停止服务"
    echo "  - 或运行: ./stop_services.sh"
    echo ""
    echo "======================================================"
}

# 主程序
main() {
    # 检查端口
    if ! check_port 5001; then
        echo "❌ 后端端口 5001 已被占用，请先停止相关服务"
        exit 1
    fi
    
    if ! check_port 3000; then
        echo "❌ 前端端口 3000 已被占用，请先停止相关服务"
        exit 1
    fi
    
    # 启动服务
    start_backend
    start_frontend
    
    # 显示使用说明
    show_usage
    
    # 等待用户中断
    echo "按 Ctrl+C 停止所有服务..."
    
    # 创建陷阱来清理进程
    trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ 服务已停止"; exit 0' INT
    
    # 等待
    wait
}

# 运行主程序
main 