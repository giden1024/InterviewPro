#!/bin/bash

echo "🚀 部署PDF解析修复到生产环境..."

# 上传修复文件到服务器
echo "📤 上传修复文件到服务器..."
scp -i ~/.ssh/aws-myy-rsa.pem Dockerfile.backend.fixed ubuntu@3.14.247.189:/home/ubuntu/InterviewPro/
scp -i ~/.ssh/aws-myy-rsa.pem docker-compose.fix.yml ubuntu@3.14.247.189:/home/ubuntu/InterviewPro/

# 连接服务器执行修复
echo "🔧 在服务器上执行修复..."
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 << 'ENDSSH'
cd /home/ubuntu/InterviewPro

echo "📋 停止当前服务..."
docker-compose down

echo "🔄 备份当前配置..."
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
cp backend/Dockerfile backend/Dockerfile.backup.$(date +%Y%m%d_%H%M%S)

echo "🔧 应用修复..."
cp Dockerfile.backend.fixed backend/Dockerfile
cp docker-compose.fix.yml docker-compose.yml

echo "🏗️ 重新构建后端镜像..."
docker-compose build --no-cache backend

echo "🚀 启动修复后的服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 30

echo "🧪 测试服务状态..."
docker-compose ps
docker logs interviewpro-backend-1 --tail 20

echo "🔍 测试PDF解析库..."
docker exec interviewpro-backend-1 python -c "
try:
    import pdfplumber
    import PyPDF2
    from docx import Document
    print('✅ PDF解析库测试成功!')
    print(f'pdfplumber: {pdfplumber.__version__}')
    print(f'PyPDF2: {PyPDF2.__version__}')
except ImportError as e:
    print('❌ PDF解析库测试失败:', e)
"

echo "✅ 部署完成!"
ENDSSH

echo "🎉 生产环境PDF解析修复部署完成!"
