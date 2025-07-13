#!/bin/bash

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 开始AWS生产环境部署...${NC}"

# 检查必要的文件
if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ 错误：.env.production 文件不存在${NC}"
    echo "请创建 .env.production 文件并配置必要的环境变量"
    exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 错误：Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ 错误：Docker Compose 未安装${NC}"
    exit 1
fi

# 1. 拉取最新代码
echo -e "${YELLOW}📥 拉取最新代码...${NC}"
git pull origin main || {
    echo -e "${RED}❌ Git pull 失败${NC}"
    exit 1
}

# 2. 备份当前运行的容器（如果存在）
echo -e "${YELLOW}💾 备份当前部署...${NC}"
if docker-compose -f docker-compose.prod.yml ps -q | grep -q .; then
    docker-compose -f docker-compose.prod.yml down
fi

# 3. 构建前端
echo -e "${YELLOW}📦 构建前端...${NC}"
cd frontend
if [ -f "package-lock.json" ]; then
    npm ci
else
    npm install
fi
npm run build || {
    echo -e "${RED}❌ 前端构建失败${NC}"
    exit 1
}
cd ..

# 4. 创建必要的目录
echo -e "${YELLOW}📁 创建必要目录...${NC}"
mkdir -p backend/uploads backend/logs backend/instance
mkdir -p nginx/logs ssl

# 5. 复制环境变量
echo -e "${YELLOW}🔧 配置环境变量...${NC}"
cp .env.production .env

# 6. 构建Docker镜像
echo -e "${YELLOW}🐳 构建Docker镜像...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache || {
    echo -e "${RED}❌ Docker构建失败${NC}"
    exit 1
}

# 7. 启动服务
echo -e "${YELLOW}🚀 启动服务...${NC}"
docker-compose -f docker-compose.prod.yml up -d || {
    echo -e "${RED}❌ 服务启动失败${NC}"
    exit 1
}

# 8. 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 30

# 9. 健康检查
echo -e "${YELLOW}🔍 进行健康检查...${NC}"

# 检查后端健康状态
for i in {1..10}; do
    if curl -f http://localhost:5001/api/v1/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务正常${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ 后端服务健康检查失败${NC}"
            echo "查看后端日志："
            docker-compose -f docker-compose.prod.yml logs backend --tail=20
            exit 1
        fi
        echo "等待后端服务启动... ($i/10)"
        sleep 10
    fi
done

# 检查前端服务
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端服务正常${NC}"
else
    echo -e "${RED}❌ 前端服务异常${NC}"
    echo "查看前端日志："
    docker-compose -f docker-compose.prod.yml logs frontend --tail=20
    exit 1
fi

# 检查nginx服务
if curl -f http://localhost/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx服务正常${NC}"
else
    echo -e "${RED}❌ Nginx服务异常${NC}"
    echo "查看Nginx日志："
    docker-compose -f docker-compose.prod.yml logs nginx --tail=20
    exit 1
fi

# 10. 显示运行状态
echo -e "${YELLOW}📊 服务状态：${NC}"
docker-compose -f docker-compose.prod.yml ps

# 11. 显示访问信息
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${BLUE}📋 访问信息：${NC}"
echo "  - HTTP:  http://$(curl -s ifconfig.me)"
echo "  - HTTPS: https://$(curl -s ifconfig.me) (需要配置SSL证书)"
echo "  - 本地:  http://localhost"

echo -e "${YELLOW}📝 后续操作：${NC}"
echo "  1. 配置域名DNS指向服务器IP"
echo "  2. 使用 ./setup-ssl.sh 配置SSL证书"
echo "  3. 配置防火墙规则"
echo "  4. 设置定期备份"

echo -e "${BLUE}🔧 管理命令：${NC}"
echo "  - 查看日志: docker-compose -f docker-compose.prod.yml logs [service]"
echo "  - 重启服务: docker-compose -f docker-compose.prod.yml restart [service]"
echo "  - 停止服务: docker-compose -f docker-compose.prod.yml down"
echo "  - 更新部署: ./deploy-aws.sh" 