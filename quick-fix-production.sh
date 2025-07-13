#!/bin/bash

echo "⚡ 快速修复生产环境PDF解析问题..."

# 直接在生产服务器的容器中安装缺失的包
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 << 'ENDSSH'
echo "🔧 在现有容器中安装PDF解析库..."

# 检查当前安装状态
echo "📋 检查当前PDF解析库状态:"
docker exec interviewpro-backend-1 python -c "
try:
    import pdfplumber
    print('✅ pdfplumber: 已安装', pdfplumber.__version__)
except ImportError as e:
    print('❌ pdfplumber: 未安装 -', e)

try:
    import PyPDF2
    print('✅ PyPDF2: 已安装', PyPDF2.__version__)
except ImportError as e:
    print('❌ PyPDF2: 未安装 -', e)
"

# 安装缺失的包
echo ""
echo "📦 安装PDF解析库..."
docker exec interviewpro-backend-1 pip install --no-cache-dir pdfplumber==0.9.0 PyPDF2==3.0.1 python-docx==0.8.11

# 验证安装
echo ""
echo "✅ 验证安装结果:"
docker exec interviewpro-backend-1 python -c "
try:
    import pdfplumber
    import PyPDF2
    from docx import Document
    print('✅ 所有PDF解析库安装成功!')
    print(f'pdfplumber: {pdfplumber.__version__}')
    print(f'PyPDF2: {PyPDF2.__version__}')
except ImportError as e:
    print('❌ 安装失败:', e)
"

# 重启后端服务
echo ""
echo "🔄 重启后端服务..."
docker restart interviewpro-backend-1

echo "⏳ 等待服务重启..."
sleep 15

echo "🧪 测试服务状态..."
docker logs interviewpro-backend-1 --tail 10

echo "✅ 快速修复完成!"
ENDSSH

echo "🎉 快速修复执行完成!"
