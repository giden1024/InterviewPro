#!/bin/bash

# InterviewPro 服务停止脚本

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 InterviewPro 服务停止脚本${NC}"
echo "======================================="

# 停止后端进程
echo -e "${YELLOW}🔍 停止后端进程...${NC}"
BACKEND_PIDS=$(pgrep -f "run_complete.py" || true)
if [ ! -z "$BACKEND_PIDS" ]; then
    echo -e "${YELLOW}⚠️  发现后端进程: $BACKEND_PIDS${NC}"
    pkill -f "run_complete.py"
    sleep 2
    echo -e "${GREEN}✅ 后端进程已停止${NC}"
else
    echo -e "${GREEN}✅ 没有发现后端进程${NC}"
fi

# 停止前端进程
echo -e "${YELLOW}🔍 停止前端进程...${NC}"
FRONTEND_PIDS=$(pgrep -f "vite.*--port.*3000" || true)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo -e "${YELLOW}⚠️  发现前端进程: $FRONTEND_PIDS${NC}"
    pkill -f "vite.*--port.*3000"
    sleep 2
    echo -e "${GREEN}✅ 前端进程已停止${NC}"
else
    echo -e "${GREEN}✅ 没有发现前端进程${NC}"
fi

echo ""
echo -e "${GREEN}🎉 所有服务已停止！${NC}" 