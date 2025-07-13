#!/bin/bash

echo "🚀 部署PDF解析修复到生产环境..."

# 设置服务器信息
SERVER_IP="3.14.247.189"
SERVER_USER="ubuntu"
PROJECT_DIR="/home/ubuntu/InterviewPro"

echo "📋 步骤1: 检查本地Docker环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

echo "✅ Docker环境检查通过"

echo ""
echo "📋 步骤2: 创建临时修复的Dockerfile..."
cat > Dockerfile.backend.fixed << 'EOF'
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    libmagic-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 首先复制requirements.txt
COPY requirements.txt .

# 分阶段安装Python依赖
# 1. 先安装基础依赖
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 2. 安装PDF解析库和其依赖
RUN pip install --no-cache-dir \
    pdfplumber==0.9.0 \
    PyPDF2==3.0.1 \
    python-docx==0.8.11

# 3. 安装其他依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/api/v1/health || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "300", "run:app"]
EOF

echo "✅ 修复的Dockerfile已创建"

echo ""
echo "📋 步骤3: 创建docker-compose覆盖文件..."
cat > docker-compose.fix.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend.fixed
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql+pymysql://interviewpro:your_password@mysql:3306/interviewpro
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=your_jwt_secret_key_here
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/instance:/app/instance
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
EOF

echo "✅ Docker Compose覆盖文件已创建"

echo ""
echo "📋 步骤4: 本地测试PDF解析修复..."
echo "构建修复的镜像..."
docker build -f Dockerfile.backend.fixed -t interviewpro-backend-fixed ./backend

echo ""
echo "📋 步骤5: 创建部署到生产环境的脚本..."
cat > deploy-to-production.sh << 'EOF'
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
EOF

chmod +x deploy-to-production.sh

echo ""
echo "📋 步骤6: 创建快速修复脚本（在容器中直接安装）..."
cat > quick-fix-production.sh << 'EOF'
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
EOF

chmod +x quick-fix-production.sh

echo ""
echo "✅ 所有修复脚本已创建完成!"
echo ""
echo "🎯 修复方案选择:"
echo "  方案1 (推荐): ./quick-fix-production.sh     - 快速在现有容器中安装包"
echo "  方案2 (彻底): ./deploy-to-production.sh     - 重新构建Docker镜像部署"
echo ""
echo "📋 本地测试命令:"
echo "  docker run --rm interviewpro-backend-fixed python -c \"import pdfplumber, PyPDF2; print('PDF解析库测试成功!')\""
echo ""
echo "⚠️  注意: 请确保有服务器SSH密钥访问权限才能执行生产环境修复" 