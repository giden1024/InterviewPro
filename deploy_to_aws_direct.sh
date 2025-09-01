#!/bin/bash

# 直接部署到AWS服务器的脚本
# 服务器: 3.138.194.143 (offerott.com)

echo "🚀 开始直接部署到AWS生产环境"
echo "📋 使用正式Creem.io API和产品ID"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# AWS服务器信息
AWS_HOST="3.138.194.143"
AWS_USER="ubuntu"
PROJECT_PATH="/home/ubuntu/InterviewPro"

echo -e "${BLUE}📋 部署配置:${NC}"
echo "  - AWS服务器: $AWS_HOST"
echo "  - 用户: $AWS_USER"
echo "  - 项目路径: $PROJECT_PATH"
echo "  - Creem API Key: creem_6AIW9sH8lsSGaAABHgfdJl"
echo "  - Basic Product ID: prod_7GCAq6iP6E27GOwil4gfDU"
echo "  - Premium Product ID: prod_2kqnPDGAScR6Ocf6ujtGi"

# 检查SSH密钥
if [[ ! -f ~/.ssh/id_rsa ]] && [[ ! -f ~/.ssh/id_ed25519 ]] && [[ -z "$SSH_KEY_PATH" ]]; then
    echo -e "${YELLOW}⚠️ 未找到SSH密钥，请确保可以SSH连接到服务器${NC}"
    echo "   可以设置环境变量: export SSH_KEY_PATH=/path/to/your/key.pem"
fi

# 1. 测试SSH连接
echo -e "${BLUE}🔗 测试SSH连接...${NC}"
if [[ -n "$SSH_KEY_PATH" ]]; then
    SSH_CMD="ssh -i $SSH_KEY_PATH -o ConnectTimeout=10"
else
    SSH_CMD="ssh -o ConnectTimeout=10"
fi

if ! $SSH_CMD $AWS_USER@$AWS_HOST "echo 'SSH连接成功'" 2>/dev/null; then
    echo -e "${RED}❌ 无法连接到AWS服务器${NC}"
    echo "   请检查:"
    echo "   1. 服务器IP是否正确: $AWS_HOST"
    echo "   2. SSH密钥是否配置正确"
    echo "   3. 服务器是否正在运行"
    exit 1
fi

echo -e "${GREEN}✅ SSH连接成功${NC}"

# 2. 创建部署包
echo -e "${BLUE}📦 创建部署包...${NC}"
DEPLOY_DIR="deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEPLOY_DIR

# 复制必要文件
cp -r backend/ $DEPLOY_DIR/
cp -r frontend/ $DEPLOY_DIR/
cp -r nginx/ $DEPLOY_DIR/
cp docker-compose.prod.yml $DEPLOY_DIR/
cp production.env $DEPLOY_DIR/
cp AWS_PRODUCTION_CREEM_DEPLOYMENT.md $DEPLOY_DIR/

# 创建服务器端部署脚本
cat > $DEPLOY_DIR/server_deploy.sh << 'EOF'
#!/bin/bash

echo "🚀 在AWS服务器上执行部署"

# 设置环境变量
export CREEM_TEST_MODE=False
export CREEM_API_KEY=creem_6AIW9sH8lsSGaAABHgfdJl
export CREEM_BASIC_PRODUCT_ID=prod_7GCAq6iP6E27GOwil4gfDU
export CREEM_PREMIUM_PRODUCT_ID=prod_2kqnPDGAScR6Ocf6ujtGi
export FRONTEND_URL=https://offerott.com
export FLASK_ENV=production
export DEBUG=False

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 清理Docker资源
echo "🧹 清理Docker资源..."
docker system prune -f

# 构建新镜像
echo "🐳 构建Docker镜像..."
if ! docker-compose -f docker-compose.prod.yml build; then
    echo "❌ Docker构建失败"
    exit 1
fi

# 启动服务
echo "🚀 启动生产服务..."
if ! docker-compose -f docker-compose.prod.yml up -d; then
    echo "❌ 服务启动失败"
    exit 1
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 检查API健康状态
echo "🏥 检查API健康状态..."
sleep 5
if curl -s -o /dev/null -w "%{http_code}" "https://offerott.com/api/v1/billing/plans" | grep -q "200"; then
    echo "✅ 后端API正常"
else
    echo "⚠️ 后端API可能还在启动中，请稍后检查"
fi

# 测试回调URL
echo "🔗 测试回调URL..."
callback_response=$(curl -s -o /dev/null -w "%{http_code}" "https://offerott.com/api/v1/billing/callback?test=1")
if [[ "$callback_response" == "400" ]]; then
    echo "✅ 回调URL可访问 (返回400是正常的)"
elif [[ "$callback_response" == "200" ]]; then
    echo "✅ 回调URL可访问"
else
    echo "⚠️ 回调URL响应码: $callback_response"
fi

# 显示最近日志
echo "📋 最近的后端日志:"
docker-compose -f docker-compose.prod.yml logs --tail=10 backend

echo ""
echo "🎉 AWS服务器部署完成!"
echo ""
echo "📋 重要信息:"
echo "  - 前端URL: https://offerott.com"
echo "  - 后端API: https://offerott.com/api/v1"
echo "  - 回调URL: https://offerott.com/api/v1/billing/callback"
echo "  - Creem测试模式: 已关闭"
echo ""
echo "📝 下一步:"
echo "  1. 在Creem.io控制台配置webhook URL: https://offerott.com/api/v1/billing/callback"
echo "  2. 测试支付流程"
echo "  3. 验证回调功能"
EOF

chmod +x $DEPLOY_DIR/server_deploy.sh

echo -e "${GREEN}✅ 部署包创建完成: $DEPLOY_DIR${NC}"

# 3. 上传到服务器
echo -e "${BLUE}📤 上传部署包到服务器...${NC}"
if ! $SSH_CMD $AWS_USER@$AWS_HOST "mkdir -p $PROJECT_PATH" 2>/dev/null; then
    echo -e "${RED}❌ 无法在服务器上创建目录${NC}"
    exit 1
fi

# 使用rsync上传文件
RSYNC_CMD="rsync -avz --delete"
if [[ -n "$SSH_KEY_PATH" ]]; then
    RSYNC_CMD="$RSYNC_CMD -e 'ssh -i $SSH_KEY_PATH'"
fi

if ! $RSYNC_CMD $DEPLOY_DIR/ $AWS_USER@$AWS_HOST:$PROJECT_PATH/; then
    echo -e "${RED}❌ 文件上传失败${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 文件上传成功${NC}"

# 4. 在服务器上执行部署
echo -e "${BLUE}🚀 在服务器上执行部署...${NC}"
$SSH_CMD $AWS_USER@$AWS_HOST "cd $PROJECT_PATH && chmod +x server_deploy.sh && ./server_deploy.sh"

# 5. 清理本地临时文件
echo -e "${BLUE}🧹 清理本地临时文件...${NC}"
rm -rf $DEPLOY_DIR

echo -e "${GREEN}🎉 部署完成!${NC}"
echo ""
echo -e "${BLUE}📋 部署后验证:${NC}"
echo "  1. 访问: https://offerott.com"
echo "  2. 测试支付: https://offerott.com/billing"
echo "  3. 查看日志: ssh $AWS_USER@$AWS_HOST 'cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml logs -f backend'"
echo ""
echo -e "${YELLOW}⚠️ 重要: 请在Creem.io控制台配置webhook URL:${NC}"
echo "   https://offerott.com/api/v1/billing/callback"
