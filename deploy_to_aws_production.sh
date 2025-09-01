#!/bin/bash

# 部署InterviewPro到AWS生产环境 (使用正式Creem.io API)
# 服务器: 3.138.194.143 (offerott.com)

echo "🚀 开始部署InterviewPro到AWS生产环境"
echo "📋 使用正式Creem.io API和产品ID"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在本地执行
if [[ "$1" == "local" ]]; then
    echo -e "${YELLOW}⚠️ 本地测试模式${NC}"
    SERVER_MODE=false
else
    echo -e "${GREEN}🌐 AWS服务器部署模式${NC}"
    SERVER_MODE=true
fi

# 1. 显示配置信息
echo -e "${BLUE}📋 生产环境配置:${NC}"
echo "  - Creem API Key: creem_6AIW9sH8lsSGaAABHgfdJl"
echo "  - Basic Product ID: prod_7GCAq6iP6E27GOwil4gfDU"
echo "  - Premium Product ID: prod_2kqnPDGAScR6Ocf6ujtGi"
echo "  - Frontend URL: https://offerott.com"
echo "  - Test Mode: False (正式环境)"

# 2. 设置环境变量
echo -e "${BLUE}⚙️ 设置生产环境变量...${NC}"
export CREEM_TEST_MODE=False
export CREEM_API_KEY=creem_6AIW9sH8lsSGaAABHgfdJl
export CREEM_BASIC_PRODUCT_ID=prod_7GCAq6iP6E27GOwil4gfDU
export CREEM_PREMIUM_PRODUCT_ID=prod_2kqnPDGAScR6Ocf6ujtGi
export FRONTEND_URL=https://offerott.com
export FLASK_ENV=production
export DEBUG=False

echo -e "${GREEN}✅ 环境变量已设置${NC}"

# 3. 备份当前配置
if [[ -f "backend/app/config.py" ]]; then
    backup_file="backend/app/config.py.backup.$(date +%Y%m%d_%H%M%S)"
    cp backend/app/config.py "$backup_file"
    echo -e "${GREEN}💾 配置已备份到: $backup_file${NC}"
fi

# 4. 检查Docker环境
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker环境检查通过${NC}"

# 5. 停止现有服务
echo -e "${BLUE}🛑 停止现有服务...${NC}"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 6. 清理旧镜像 (可选)
echo -e "${BLUE}🧹 清理Docker资源...${NC}"
docker system prune -f

# 7. 构建新镜像
echo -e "${BLUE}🐳 构建Docker镜像...${NC}"
if ! docker-compose -f docker-compose.prod.yml build; then
    echo -e "${RED}❌ Docker构建失败${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker镜像构建成功${NC}"

# 8. 启动服务
echo -e "${BLUE}🚀 启动生产服务...${NC}"
if ! docker-compose -f docker-compose.prod.yml up -d; then
    echo -e "${RED}❌ 服务启动失败${NC}"
    exit 1
fi

# 9. 等待服务启动
echo -e "${BLUE}⏳ 等待服务启动...${NC}"
sleep 15

# 10. 检查服务状态
echo -e "${BLUE}📊 检查服务状态...${NC}"
docker-compose -f docker-compose.prod.yml ps

# 11. 检查服务健康状态
echo -e "${BLUE}🏥 检查服务健康状态...${NC}"

# 检查后端API
if curl -s -o /dev/null -w "%{http_code}" "https://offerott.com/api/v1/billing/plans" | grep -q "200"; then
    echo -e "${GREEN}✅ 后端API正常${NC}"
else
    echo -e "${YELLOW}⚠️ 后端API可能还在启动中${NC}"
fi

# 检查前端
if curl -s -o /dev/null -w "%{http_code}" "https://offerott.com" | grep -q "200"; then
    echo -e "${GREEN}✅ 前端服务正常${NC}"
else
    echo -e "${YELLOW}⚠️ 前端服务可能还在启动中${NC}"
fi

# 12. 测试Creem回调URL
echo -e "${BLUE}🔗 测试Creem回调URL...${NC}"
callback_url="https://offerott.com/api/v1/billing/callback"
callback_response=$(curl -s -o /dev/null -w "%{http_code}" "$callback_url?test=1")

if [[ "$callback_response" == "400" ]]; then
    echo -e "${GREEN}✅ 回调URL可访问 (返回400是正常的，缺少必需参数)${NC}"
elif [[ "$callback_response" == "200" ]]; then
    echo -e "${GREEN}✅ 回调URL可访问${NC}"
else
    echo -e "${YELLOW}⚠️ 回调URL响应码: $callback_response${NC}"
fi

# 13. 显示日志 (最近20行)
echo -e "${BLUE}📋 最近的后端日志:${NC}"
docker-compose -f docker-compose.prod.yml logs --tail=20 backend

# 14. 显示重要信息
echo ""
echo -e "${GREEN}🎉 部署完成!${NC}"
echo ""
echo -e "${BLUE}📋 重要信息:${NC}"
echo "  - 前端URL: https://offerott.com"
echo "  - 后端API: https://offerott.com/api/v1"
echo "  - 回调URL: https://offerott.com/api/v1/billing/callback"
echo "  - Creem测试模式: 已关闭 (使用正式API)"
echo "  - API密钥: creem_6AIW9sH8lsSGaAABHgfdJl"
echo ""
echo -e "${BLUE}📝 下一步操作:${NC}"
echo "  1. 在Creem.io控制台配置webhook URL:"
echo "     https://offerott.com/api/v1/billing/callback"
echo "  2. 确保webhook事件包括: checkout.completed, payment.completed"
echo "  3. 测试支付流程验证回调"
echo ""
echo -e "${BLUE}🔧 有用的命令:${NC}"
echo "  查看日志: docker-compose -f docker-compose.prod.yml logs -f backend"
echo "  重启服务: docker-compose -f docker-compose.prod.yml restart"
echo "  停止服务: docker-compose -f docker-compose.prod.yml down"
echo ""
echo -e "${GREEN}🔗 测试URL:${NC}"
echo "  - 支付页面: https://offerott.com/billing"
echo "  - API健康检查: https://offerott.com/api/v1/billing/plans"
