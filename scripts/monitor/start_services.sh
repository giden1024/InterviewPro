#!/bin/bash

# InterviewPro 服务启动脚本
# 统一端口配置：前端3000，后端5001

set -e

PROJECT_ROOT="/Users/mayuyang/InterviewPro"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 InterviewPro 服务启动脚本${NC}"
echo "======================================="

# 检查并停止现有进程
echo -e "${YELLOW}🔍 检查现有进程...${NC}"

# 停止现有的后端进程
BACKEND_PIDS=$(pgrep -f "run_complete.py" || true)
if [ ! -z "$BACKEND_PIDS" ]; then
    echo -e "${YELLOW}⚠️  发现现有后端进程: $BACKEND_PIDS${NC}"
    pkill -f "run_complete.py" || true
    sleep 2
    echo -e "${GREEN}✅ 后端进程已停止${NC}"
fi

# 停止现有的前端进程
FRONTEND_PIDS=$(pgrep -f "vite.*--port.*3000" || true)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo -e "${YELLOW}⚠️  发现现有前端进程: $FRONTEND_PIDS${NC}"
    pkill -f "vite.*--port.*3000" || true
    sleep 2
    echo -e "${GREEN}✅ 前端进程已停止${NC}"
fi

echo ""

# 启动后端服务
echo -e "${BLUE}🔧 启动后端服务 (端口 5001)...${NC}"
cd "$BACKEND_DIR"

# 激活虚拟环境并启动后端
source "$PROJECT_ROOT/venv/bin/activate"
nohup python run_complete.py > backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:5001/health > /dev/null; then
    echo -e "${GREEN}✅ 后端健康检查通过${NC}"
else
    echo -e "${RED}❌ 后端启动失败，请检查日志${NC}"
    tail -10 backend.log
    exit 1
fi

echo ""

# 启动前端服务
echo -e "${BLUE}🌐 启动前端服务 (端口 3000)...${NC}"
cd "$FRONTEND_DIR"

# 启动前端开发服务器
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
sleep 5

# 检查前端是否启动成功
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ 前端健康检查通过${NC}"
else
    echo -e "${RED}❌ 前端启动失败，请检查日志${NC}"
    tail -10 frontend.log
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 所有服务启动成功！${NC}"
echo "======================================="
echo -e "${BLUE}📋 服务信息:${NC}"
echo -e "  • 前端: http://localhost:3000 (PID: $FRONTEND_PID)"
echo -e "  • 后端: http://localhost:5001 (PID: $BACKEND_PID)"
echo ""
echo -e "${BLUE}📊 实时监控:${NC}"
echo -e "  • 后端日志: tail -f $BACKEND_DIR/backend.log"
echo -e "  • 前端日志: tail -f $FRONTEND_DIR/frontend.log"
echo ""
echo -e "${BLUE}🔧 管理命令:${NC}"
echo -e "  • 停止服务: ./stop_services.sh"
echo -e "  • 查看状态: ./check_services.sh"
echo ""
echo -e "${YELLOW}💡 提示: 服务正在后台运行，可以关闭此终端${NC}" 