# InterviewPro AWS部署指南

## 🌟 部署架构

```
Internet → CloudFront → ALB → EC2 (Docker) → RDS PostgreSQL
                              ↓
                         S3 (静态文件)
```

## 🛠️ 1. AWS服务器初始化

### 1.1 EC2实例配置
- **实例类型**: t3.medium (2 vCPU, 4GB RAM)
- **操作系统**: Ubuntu 22.04 LTS
- **存储**: 20GB gp3
- **安全组**: 开放端口 22, 80, 443, 5001, 3000

### 1.2 连接到服务器并安装基础环境

```bash
# 连接到EC2实例
ssh -i your-key.pem ubuntu@your-ec2-ip

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装Node.js和Python
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs python3 python3-pip git nginx

# 重新登录以应用docker组权限
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

## 🐳 2. Docker化部署

### 2.1 创建生产环境Docker配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/interviewpro
      - JWT_SECRET_KEY=your-super-secret-jwt-key
      - CORS_ORIGINS=https://your-domain.com
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/logs:/app/logs
    restart: unless-stopped
    depends_on:
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "3000:80"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### 2.2 后端生产Dockerfile

```dockerfile
# backend/Dockerfile.prod
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p uploads logs instance

# 设置环境变量
ENV FLASK_APP=run_complete.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "run_complete:app"]
```

### 2.3 前端生产Dockerfile

```dockerfile
# frontend/Dockerfile.prod
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🌐 3. Nginx配置

### 3.1 生产环境Nginx配置

```nginx
# nginx/nginx.prod.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5001;
    }

    upstream frontend {
        server frontend:80;
    }

    # HTTP重定向到HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS主服务器
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        # 前端路由
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API路由
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket支持
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # 静态文件缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            proxy_pass http://frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 🗄️ 4. 数据库配置 (RDS)

### 4.1 创建RDS PostgreSQL实例

```bash
# AWS CLI创建RDS实例
aws rds create-db-instance \
    --db-instance-identifier interviewpro-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password YourSecurePassword123! \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxx \
    --db-name interviewpro \
    --backup-retention-period 7 \
    --multi-az \
    --storage-encrypted
```

### 4.2 数据库初始化脚本

```python
# scripts/init_production_db.py
import os
import sys
sys.path.append('/app')

from app import create_app
from app.extensions import db
from app.models import User, Resume, Question, InterviewSession, Answer

def init_production_database():
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功")
        
        # 创建管理员用户
        admin_user = User(
            email='admin@interviewpro.com',
            name='Administrator'
        )
        admin_user.set_password('AdminPassword123!')
        db.session.add(admin_user)
        db.session.commit()
        print("✅ 管理员用户创建成功")

if __name__ == '__main__':
    init_production_database()
```

## 🚀 5. 部署脚本

### 5.1 自动化部署脚本

```bash
#!/bin/bash
# deploy-aws.sh

set -e

echo "🚀 开始AWS生产环境部署..."

# 1. 拉取最新代码
git pull origin main

# 2. 构建前端
echo "📦 构建前端..."
cd frontend
npm ci
npm run build
cd ..

# 3. 更新环境变量
echo "🔧 配置环境变量..."
cp .env.production .env

# 4. 构建并启动Docker容器
echo "🐳 构建Docker镜像..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 5. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 6. 初始化数据库
echo "🗄️ 初始化数据库..."
docker-compose -f docker-compose.prod.yml exec backend python scripts/init_production_db.py

# 7. 健康检查
echo "🔍 进行健康检查..."
if curl -f http://localhost:5001/api/v1/health; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
    exit 1
fi

if curl -f http://localhost:3000; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
    exit 1
fi

echo "🎉 部署完成！"
echo "🌐 访问地址: https://your-domain.com"
```

### 5.2 环境变量配置

```bash
# .env.production
FLASK_ENV=production
DATABASE_URL=postgresql://admin:YourSecurePassword123!@your-rds-endpoint.amazonaws.com:5432/interviewpro
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Redis配置
REDIS_URL=redis://redis:6379/0

# 文件上传配置
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=16777216

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# AWS配置
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=interviewpro-uploads
AWS_REGION=us-east-1
```

## 🔒 6. SSL证书配置

### 6.1 使用Let's Encrypt免费SSL

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 7. 监控和日志

### 7.1 日志管理

```yaml
# docker-compose.prod.yml 中添加日志配置
version: '3.8'
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 7.2 健康检查端点

```python
# backend/app/api/health.py
from flask import Blueprint, jsonify
import psutil
import redis

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    try:
        # 检查数据库连接
        from app.extensions import db
        db.session.execute('SELECT 1')
        
        # 检查Redis连接
        r = redis.Redis(host='redis', port=6379, db=0)
        r.ping()
        
        # 系统资源检查
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'redis': 'connected',
            'cpu_usage': f"{cpu_percent}%",
            'memory_usage': f"{memory_percent}%"
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

## 🔄 8. CI/CD配置 (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.AWS_HOST }}
        username: ubuntu
        key: ${{ secrets.AWS_SSH_KEY }}
        script: |
          cd /home/ubuntu/InterviewPro
          ./deploy-aws.sh
```

## 📋 9. 部署检查清单

- [ ] EC2实例配置完成
- [ ] RDS数据库创建完成
- [ ] 域名DNS配置完成
- [ ] SSL证书安装完成
- [ ] 环境变量配置完成
- [ ] Docker容器运行正常
- [ ] 数据库初始化完成
- [ ] 健康检查通过
- [ ] 监控配置完成
- [ ] 备份策略设置完成

## 🆘 10. 故障排除

### 常见问题解决方案

1. **容器启动失败**
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend
   ```

2. **数据库连接失败**
   - 检查RDS安全组配置
   - 验证数据库连接字符串

3. **SSL证书问题**
   ```bash
   sudo certbot certificates
   sudo nginx -t
   ```

4. **性能优化**
   ```bash
   # 查看资源使用情况
   docker stats
   htop
   ``` 