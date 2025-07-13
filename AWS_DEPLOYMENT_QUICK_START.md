# AWS部署快速开始指南

## 🚀 快速部署步骤

### 1. 准备AWS服务器

#### 1.1 创建EC2实例
```bash
# 推荐配置
实例类型: t3.medium (2 vCPU, 4GB RAM)
操作系统: Ubuntu 22.04 LTS
存储: 20GB gp3
安全组: 开放端口 22, 80, 443
```

#### 1.2 连接服务器并安装环境
```bash
# 连接到EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# 一键安装环境
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs python3 python3-pip git nginx
```

### 2. 部署应用代码

#### 2.1 克隆代码
```bash
git clone https://github.com/your-username/InterviewPro.git
cd InterviewPro
```

#### 2.2 配置环境变量
```bash
# 复制配置模板
cp env.production.template .env.production

# 编辑配置文件
nano .env.production
```

**必须修改的配置项：**
```bash
# 数据库连接（如果使用RDS）
DATABASE_URL=postgresql://admin:YourPassword@your-rds-endpoint.amazonaws.com:5432/interviewpro

# JWT密钥（请生成随机字符串）
JWT_SECRET_KEY=your-super-secret-jwt-key-please-change-this

# 域名配置
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

#### 2.3 一键部署
```bash
./deploy-aws.sh
```

### 3. 配置SSL证书（可选但推荐）

#### 3.1 配置域名DNS
将您的域名A记录指向EC2公网IP

#### 3.2 获取SSL证书
```bash
./setup-ssl.sh your-domain.com www.your-domain.com
```

### 4. 验证部署

#### 4.1 检查服务状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

#### 4.2 访问应用
- HTTP: `http://your-ec2-ip`
- HTTPS: `https://your-domain.com` (如果配置了SSL)

#### 4.3 健康检查
```bash
curl http://your-ec2-ip/api/v1/health
```

## 🗄️ 数据库选项

### 选项1: 使用SQLite（简单）
```bash
# 在.env.production中设置
DATABASE_URL=sqlite:///instance/interview.db
```

### 选项2: 使用AWS RDS PostgreSQL（推荐）
```bash
# 创建RDS实例
aws rds create-db-instance \
    --db-instance-identifier interviewpro-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password YourSecurePassword123! \
    --allocated-storage 20 \
    --db-name interviewpro

# 在.env.production中配置
DATABASE_URL=postgresql://admin:YourSecurePassword123!@your-rds-endpoint.amazonaws.com:5432/interviewpro
```

## 📋 部署检查清单

- [ ] ✅ EC2实例创建并配置安全组
- [ ] ✅ 服务器环境安装完成
- [ ] ✅ 代码克隆到服务器
- [ ] ✅ 环境变量配置完成
- [ ] ✅ 部署脚本执行成功
- [ ] ✅ 所有Docker容器运行正常
- [ ] ✅ 健康检查通过
- [ ] ✅ 域名DNS配置（如果有域名）
- [ ] ✅ SSL证书配置（推荐）

## 🔧 常用管理命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs nginx

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 更新部署
git pull origin main
./deploy-aws.sh

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 数据库管理
docker-compose -f docker-compose.prod.yml exec backend python scripts/init_production_db.py --check
```

## 🚨 故障排除

### 问题1: 容器启动失败
```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs backend --tail=50

# 检查环境变量
docker-compose -f docker-compose.prod.yml exec backend env | grep -E "(DATABASE|JWT|CORS)"
```

### 问题2: 数据库连接失败
```bash
# 检查数据库连接
docker-compose -f docker-compose.prod.yml exec backend python -c "
import os
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
"

# 测试数据库连接
docker-compose -f docker-compose.prod.yml exec backend python scripts/init_production_db.py --check
```

### 问题3: 前端无法访问后端API
```bash
# 检查nginx配置
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# 检查CORS配置
curl -H "Origin: https://your-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://your-ec2-ip/api/v1/health
```

### 问题4: SSL证书问题
```bash
# 检查证书状态
sudo certbot certificates

# 测试nginx配置
sudo nginx -t

# 手动续期证书
sudo certbot renew --dry-run
```

## 📞 技术支持

如果遇到部署问题，请检查：

1. **系统资源**: 确保服务器有足够的内存和磁盘空间
2. **网络配置**: 检查安全组和防火墙设置
3. **环境变量**: 确保所有必需的环境变量都已正确配置
4. **日志文件**: 查看详细的错误日志定位问题

## 🔄 自动化部署（可选）

设置GitHub Actions自动部署：

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
          git pull origin main
          ./deploy-aws.sh
``` 