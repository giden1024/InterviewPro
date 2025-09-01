#!/bin/bash

# InterviewPro快速部署脚本
# 基于现有AWS服务器和部署脚本

echo "🚀 InterviewPro生产环境快速部署"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 服务器信息
AWS_HOST="3.138.194.143"
AWS_USER="ec2-user"
DOMAIN="offerott.com"

echo -e "${BLUE}📋 部署信息:${NC}"
echo "  - 服务器: $AWS_HOST ($DOMAIN)"
echo "  - Creem API: 正式环境 (creem_6AIW9sH8lsSGaAABHgfdJl)"
echo "  - 产品ID: Basic(prod_7GCAq6iP6E27GOwil4gfDU), Premium(prod_2kqnPDGAScR6Ocf6ujtGi)"
echo ""

# 检查SSH连接
echo -e "${BLUE}🔗 检查服务器连接...${NC}"
SSH_KEY="/Users/mayuyang/InterviewPro/aws-myy-rsa.pem"
if ssh -i $SSH_KEY -o ConnectTimeout=10 -o BatchMode=yes $AWS_USER@$AWS_HOST "echo 'SSH连接成功'" 2>/dev/null; then
    echo -e "${GREEN}✅ 服务器连接正常${NC}"
else
    echo -e "${RED}❌ 无法连接到服务器${NC}"
    echo "请确保:"
    echo "  1. SSH密钥文件存在: $SSH_KEY"
    echo "  2. 服务器可访问: ping $AWS_HOST"
    echo "  3. 用户名正确: $AWS_USER"
    exit 1
fi

# 检查项目是否已存在于服务器
echo -e "${BLUE}📁 检查服务器项目状态...${NC}"
PROJECT_EXISTS=$(ssh -i $SSH_KEY $AWS_USER@$AWS_HOST "[ -d '/home/ec2-user/InterviewPro' ] && echo 'exists' || echo 'not_exists'")

if [ "$PROJECT_EXISTS" = "exists" ]; then
    echo -e "${GREEN}✅ 项目目录已存在，将更新代码${NC}"
    DEPLOYMENT_MODE="update"
else
    echo -e "${YELLOW}⚠️ 项目目录不存在，需要完整部署${NC}"
    DEPLOYMENT_MODE="full"
fi

# 执行部署
echo -e "${BLUE}🚀 开始部署...${NC}"

if [ "$DEPLOYMENT_MODE" = "update" ]; then
    # 更新部署
    echo "📥 更新现有项目..."
    ssh -i $SSH_KEY $AWS_USER@$AWS_HOST << 'EOF'
        set -e
        cd /home/ec2-user/InterviewPro
        
        echo "📥 更新代码..."
        git pull origin main
        
        echo "🛑 停止现有服务..."
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
        
        echo "🐳 重新构建服务..."
        docker-compose -f docker-compose.prod.yml build --no-cache
        
        echo "🚀 启动服务..."
        docker-compose -f docker-compose.prod.yml up -d
        
        echo "⏳ 等待服务启动..."
        sleep 15
        
        echo "📊 检查服务状态..."
        docker-compose -f docker-compose.prod.yml ps
EOF
else
    # 完整部署
    echo "📦 执行完整部署..."
    
    # 创建部署包
    echo "📦 创建部署包..."
    TEMP_DIR="deploy_$(date +%Y%m%d_%H%M%S)"
    mkdir -p $TEMP_DIR
    
    # 复制关键文件
    cp -r backend/ $TEMP_DIR/ 2>/dev/null || echo "backend目录不存在，跳过"
    cp -r frontend/ $TEMP_DIR/ 2>/dev/null || echo "frontend目录不存在，跳过"
    cp -r nginx/ $TEMP_DIR/ 2>/dev/null || echo "nginx目录不存在，跳过"
    cp docker-compose.prod.yml $TEMP_DIR/ 2>/dev/null || echo "docker-compose.prod.yml不存在"
    cp production.env $TEMP_DIR/ 2>/dev/null || echo "production.env不存在"
    cp -r scripts/ $TEMP_DIR/ 2>/dev/null || echo "scripts目录不存在，跳过"
    
    # 上传到服务器
    echo "📤 上传到服务器..."
    rsync -avz --delete -e "ssh -i $SSH_KEY" $TEMP_DIR/ $AWS_USER@$AWS_HOST:/home/ec2-user/InterviewPro/
    
    # 在服务器上执行部署
    ssh -i $SSH_KEY $AWS_USER@$AWS_HOST << 'EOF'
        set -e
        cd /home/ec2-user/InterviewPro
        
        echo "🔧 设置执行权限..."
        find scripts/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
        chmod +x deploy_to_aws_production.sh 2>/dev/null || true
        
        echo "🐳 构建Docker服务..."
        docker-compose -f docker-compose.prod.yml build --no-cache
        
        echo "🚀 启动服务..."
        docker-compose -f docker-compose.prod.yml up -d
        
        echo "⏳ 等待服务启动..."
        sleep 20
        
        echo "📊 检查服务状态..."
        docker-compose -f docker-compose.prod.yml ps
EOF
    
    # 清理临时文件
    rm -rf $TEMP_DIR
fi

# 验证部署
echo -e "${BLUE}🔍 验证部署...${NC}"
sleep 5

# 检查服务状态
echo "📊 检查Docker服务..."
ssh -i $SSH_KEY $AWS_USER@$AWS_HOST "cd /home/ec2-user/InterviewPro && docker-compose -f docker-compose.prod.yml ps"

# 测试API端点
echo "🌐 测试API端点..."
if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/api/v1/billing/plans" | grep -q "200"; then
    echo -e "${GREEN}✅ API端点正常${NC}"
else
    echo -e "${YELLOW}⚠️ API端点可能还在启动中${NC}"
fi

# 测试回调URL
echo "🔗 测试回调URL..."
callback_code=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/api/v1/billing/callback?test=1")
if [[ "$callback_code" == "400" || "$callback_code" == "200" ]]; then
    echo -e "${GREEN}✅ 回调URL可访问 (状态码: $callback_code)${NC}"
else
    echo -e "${YELLOW}⚠️ 回调URL状态码: $callback_code${NC}"
fi

# 显示部署结果
echo ""
echo -e "${GREEN}🎉 部署完成!${NC}"
echo "================================"
echo -e "${BLUE}📋 访问信息:${NC}"
echo "  - 前端: https://$DOMAIN"
echo "  - 后端API: https://$DOMAIN/api/v1"
echo "  - 支付页面: https://$DOMAIN/billing"
echo "  - 回调URL: https://$DOMAIN/api/v1/billing/callback"
echo ""
echo -e "${BLUE}📝 下一步:${NC}"
echo "  1. 在Creem.io控制台配置webhook URL: https://$DOMAIN/api/v1/billing/callback"
echo "  2. 测试支付流程: https://$DOMAIN/billing"
echo "  3. 监控回调日志: ssh $AWS_USER@$AWS_HOST 'cd /home/ubuntu/InterviewPro && docker-compose -f docker-compose.prod.yml logs -f backend | grep CALLBACK'"
echo ""
echo -e "${YELLOW}⚠️ 重要提醒:${NC}"
echo "  - 现在使用的是正式Creem.io API，不再是测试模式"
echo "  - 回调问题应该得到解决，因为使用了稳定的域名和正式API"
echo "  - 如有问题，请查看服务器日志进行排查"
