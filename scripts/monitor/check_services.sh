#!/bin/bash

# InterviewPro 服务状态检查脚本

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 InterviewPro 服务状态检查${NC}"
echo "======================================="

# 检查后端进程
echo -e "${BLUE}🔧 后端服务状态:${NC}"
BACKEND_PIDS=$(pgrep -f "run_complete.py" || true)
if [ ! -z "$BACKEND_PIDS" ]; then
    echo -e "${GREEN}✅ 后端进程运行中 (PID: $BACKEND_PIDS)${NC}"
    
    # 检查后端健康状态
    if curl -s http://localhost:5001/health > /dev/null; then
        echo -e "${GREEN}✅ 后端健康检查通过 (http://localhost:5001)${NC}"
    else
        echo -e "${RED}❌ 后端健康检查失败${NC}"
    fi
else
    echo -e "${RED}❌ 后端进程未运行${NC}"
fi

echo ""

# 检查前端进程
echo -e "${BLUE}🌐 前端服务状态:${NC}"
FRONTEND_PIDS=$(pgrep -f "vite.*--port.*3000" || true)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo -e "${GREEN}✅ 前端进程运行中 (PID: $FRONTEND_PIDS)${NC}"
    
    # 检查前端健康状态
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✅ 前端健康检查通过 (http://localhost:3000)${NC}"
    else
        echo -e "${RED}❌ 前端健康检查失败${NC}"
    fi
else
    echo -e "${RED}❌ 前端进程未运行${NC}"
fi

echo ""

# 端口占用情况
echo -e "${BLUE}🔌 端口占用情况:${NC}"
echo -e "${YELLOW}端口 3000 (前端):${NC}"
lsof -i :3000 || echo -e "${RED}  端口 3000 未被占用${NC}"

echo -e "${YELLOW}端口 5001 (后端):${NC}"
lsof -i :5001 || echo -e "${RED}  端口 5001 未被占用${NC}"

echo ""
echo -e "${BLUE}💡 管理命令:${NC}"
echo -e "  • 启动服务: ./start_services.sh"
echo -e "  • 停止服务: ./stop_services.sh" 