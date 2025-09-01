#!/bin/bash

# InterviewPro 服务启动脚本
# 自动启动后端、前端和Browser Tools MCP服务

echo "🚀 InterviewPro 服务启动脚本"
echo "=================================="

# 检查依赖
echo "📋 检查依赖..."

# 检查Python虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 未找到虚拟环境，请先运行: python3 -m venv venv"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ 未找到前端依赖，请先运行: cd frontend && npm install"
    exit 1
fi

echo "✅ 依赖检查通过"

# 激活虚拟环境
echo "🔧 激活Python虚拟环境..."
source venv/bin/activate

# 检查后端依赖
echo "🔧 检查后端依赖..."
cd backend
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ 后端依赖未安装，请先运行: pip install -r requirements.txt"
    exit 1
fi

# 启动后端服务
echo "🚀 启动后端服务..."
python run_complete.py &
BACKEND_PID=$!
echo "📡 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端健康状态
if curl -s http://localhost:5001/health > /dev/null; then
    echo "✅ 后端服务健康检查通过"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID
    exit 1
fi

# 启动前端服务
echo "🚀 启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "📡 前端服务已启动 (PID: $FRONTEND_PID)"

# 等待前端启动
echo "⏳ 等待前端服务启动..."
sleep 3

# 启动Browser Tools MCP
echo "🚀 启动Browser Tools MCP..."
npm exec @agentdeskai/browser-tools-mcp@1.2.0 &
MCP_PID=$!
echo "📡 Browser Tools MCP已启动 (PID: $MCP_PID)"

echo "=================================="
echo "✅ 所有服务已启动成功!"
echo "🌐 前端访问: http://localhost:3000"
echo "🔧 后端API: http://localhost:5001"
echo "❤️ 健康检查: http://localhost:5001/health"
echo "🛠️ Browser Tools: 自动配置"
echo "=================================="
echo "💡 提示: 在浏览器中访问 http://localhost:3000 开始使用"
echo "🔍 调试: 查看后端日志和前端控制台"
echo "=================================="

# 等待用户输入退出
echo "按 Ctrl+C 或回车键停止所有服务..."
read -p ""

# 停止所有服务
echo "🛑 正在停止所有服务..."
kill $BACKEND_PID $FRONTEND_PID $MCP_PID 2>/dev/null

echo "✅ 所有服务已停止"
echo "�� 感谢使用InterviewPro!" 