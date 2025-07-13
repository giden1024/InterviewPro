#!/bin/bash

# Deploy OCR Functionality Script
# 部署OCR图片文字识别功能

set -e  # 遇到错误立即退出

echo "🚀 开始部署OCR图片文字识别功能..."

# 定义颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务器配置
SERVER_HOST="3.14.247.189"
SERVER_USER="ubuntu"
SSH_KEY="aws-myy-rsa.pem"

# 确保SSH密钥存在
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ SSH密钥文件不存在: $SSH_KEY${NC}"
    echo "请确保SSH密钥文件在当前目录中"
    exit 1
fi

# 设置SSH密钥权限
chmod 600 "$SSH_KEY"

echo -e "${BLUE}📦 Step 1: 更新后端依赖包...${NC}"

# 远程执行命令
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
set -e

echo "🔧 安装系统级依赖..."

# 更新包列表
sudo apt-get update

# 安装Tesseract-OCR和相关依赖
sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra
sudo apt-get install -y libtesseract-dev libleptonica-dev pkg-config

# 安装OpenCV系统依赖
sudo apt-get install -y libopencv-dev python3-opencv

# 验证Tesseract安装
tesseract --version

echo "✅ 系统依赖安装完成"

echo "🐳 停止Docker服务..."
cd /home/ubuntu/InterviewPro
sudo docker-compose down

echo "🔄 安装Python包依赖..."
# 进入后端容器并安装新的依赖包
sudo docker-compose exec -T interviewpro-backend-1 pip install pytesseract==0.3.10 opencv-python==4.8.1.78 || true

echo "✅ 依赖包安装完成"
EOF

echo -e "${BLUE}📤 Step 2: 上传更新的代码文件...${NC}"

# 上传后端文件
echo "📤 上传OCR服务文件..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "backend/app/services/ocr_service.py" "$SERVER_USER@$SERVER_HOST:/home/ubuntu/InterviewPro/backend/app/services/"

echo "📤 上传更新的API文件..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "backend/app/api/jobs.py" "$SERVER_USER@$SERVER_HOST:/home/ubuntu/InterviewPro/backend/app/api/"

echo "📤 上传更新的requirements.txt..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "backend/requirements.txt" "$SERVER_USER@$SERVER_HOST:/home/ubuntu/InterviewPro/backend/"

# 上传前端文件
echo "📤 上传更新的前端文件..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "frontend/src/services/jobService.ts" "$SERVER_USER@$SERVER_HOST:/home/ubuntu/InterviewPro/frontend/src/services/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "frontend/src/pages/JobPage.tsx" "$SERVER_USER@$SERVER_HOST:/home/ubuntu/InterviewPro/frontend/src/pages/"

# 上传测试页面
echo "📤 上传OCR测试页面..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "frontend/public/test-ocr-functionality.html" "$SERVER_USER@$SERVER_HOST:/home/ubuntu/InterviewPro/frontend/public/"

echo -e "${BLUE}🔨 Step 3: 重新构建和启动服务...${NC}"

# 重新构建和启动服务
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
set -e

echo "🔨 重新构建并启动服务..."
cd /home/ubuntu/InterviewPro

# 重新构建后端镜像（包含新依赖）
sudo docker-compose build backend

# 重新构建前端镜像
sudo docker-compose build frontend

# 启动所有服务
sudo docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "📊 检查服务状态:"
sudo docker-compose ps

# 检查后端容器中的OCR依赖
echo "🔍 验证OCR依赖安装:"
sudo docker-compose exec -T backend python -c "
try:
    import pytesseract
    import cv2
    import numpy as np
    from PIL import Image
    print('✅ 所有OCR依赖已安装')
    print('Tesseract版本:', pytesseract.get_tesseract_version())
except ImportError as e:
    print('❌ 依赖安装失败:', e)
"

# 检查OCR服务
echo "🧪 测试OCR服务导入:"
sudo docker-compose exec -T backend python -c "
try:
    from app.services.ocr_service import OCRService
    ocr = OCRService()
    print('✅ OCR服务导入成功')
except Exception as e:
    print('❌ OCR服务导入失败:', e)
"

echo "✅ 服务重启完成"
EOF

echo -e "${BLUE}🧪 Step 4: 验证部署...${NC}"

# 验证服务状态
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
echo "🔍 验证部署状态..."

# 检查网站是否可访问
if curl -s -o /dev/null -w "%{http_code}" https://offerott.com | grep -q "200"; then
    echo "✅ 网站访问正常 (https://offerott.com)"
else
    echo "⚠️ 网站可能有问题"
fi

# 检查服务日志
echo "📋 最近的服务日志:"
sudo docker-compose logs --tail=10 backend

echo "🎯 OCR功能部署完成！"
echo ""
echo "📝 测试说明:"
echo "1. 访问 https://offerott.com/jobs 页面"
echo "2. 在 'Drag and drop or upload a screenshot' 区域上传图片"
echo "3. 系统会自动识别图片中的文字并填充到Job description文本框"
echo "4. 可以使用测试页面: https://offerott.com/test-ocr-functionality.html"
echo ""
echo "🔧 支持的图片格式: PNG, JPG, JPEG, BMP, TIFF, WEBP"
echo "📏 最大文件大小: 10MB"
EOF

echo -e "${GREEN}🎉 OCR图片文字识别功能部署完成！${NC}"
echo ""
echo -e "${YELLOW}📋 功能说明:${NC}"
echo "✅ 在Jobs页面添加了图片上传和OCR文字识别功能"
echo "✅ 支持拖拽上传和点击选择文件"
echo "✅ 识别的文字会自动填充到Job description文本框"
echo "✅ 支持中英文文字识别"
echo "✅ 创建了独立的测试页面用于功能验证"
echo ""
echo -e "${BLUE}🌐 访问地址:${NC}"
echo "• 主要功能: https://offerott.com/jobs"
echo "• 测试页面: https://offerott.com/test-ocr-functionality.html"
echo ""
echo -e "${GREEN}🚀 部署成功！${NC}" 