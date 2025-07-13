#!/bin/bash

echo "🔧 修复PDF解析库问题..."

# 检查Docker容器是否运行
echo "📋 检查当前Docker容器状态..."
docker ps | grep interviewpro

echo ""
echo "🐳 进入后端容器检查Python包安装情况..."

# 检查PDF解析库安装状态
echo "检查pdfplumber和PyPDF2安装状态:"
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

try:
    from docx import Document
    print('✅ python-docx: 已安装')
except ImportError as e:
    print('❌ python-docx: 未安装 -', e)
"

echo ""
echo "🔧 方案1: 在容器中直接安装缺失的包..."
echo "安装PDF解析库..."

docker exec interviewpro-backend-1 pip install pdfplumber==0.9.0 PyPDF2==3.0.1 python-docx==0.8.11

echo ""
echo "📋 验证安装结果..."
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

echo ""
echo "🔄 重启后端服务以应用更改..."
docker restart interviewpro-backend-1

echo ""
echo "⏳ 等待服务重启..."
sleep 10

echo ""
echo "🧪 测试PDF解析功能..."
curl -s -X POST https://offerott.com/api/v1/resumes/6/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"include_suggestions":true,"include_score":true}' | jq

echo ""
echo "✅ PDF解析库修复完成!"
echo ""
echo "📝 如果问题仍然存在，请使用方案2重新构建Docker镜像:"
echo "   docker-compose down"
echo "   docker-compose build --no-cache backend"
echo "   docker-compose up -d" 