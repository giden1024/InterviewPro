# 手动部署包 - InterviewPro生产环境

## 🚨 SSH连接问题解决方案

由于SSH密钥连接问题，我们提供手动部署方案。

## 📦 部署包内容

### 1. 创建部署包
```bash
# 在本地执行
tar -czf interviewpro-production-$(date +%Y%m%d_%H%M%S).tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='backend/instance' \
    --exclude='frontend/dist' \
    backend/ \
    frontend/ \
    nginx/ \
    docker-compose.prod.yml \
    production.env \
    AWS_PRODUCTION_CREEM_DEPLOYMENT.md \
    FINAL_DEPLOYMENT_PLAN.md
```

### 2. 上传到服务器
有几种上传方式：

#### 方式A: 使用SCP (如果SSH工作)
```bash
scp -i aws-myy-rsa.pem interviewpro-production-*.tar.gz ubuntu@3.138.194.143:/home/ubuntu/
```

#### 方式B: 使用AWS控制台
1. 登录AWS控制台
2. 找到EC2实例 (3.138.194.143)
3. 使用"Session Manager"连接
4. 通过S3或其他方式传输文件

#### 方式C: 使用Git (推荐)
在服务器上直接拉取代码：
```bash
# 在服务器上执行
cd /home/ubuntu
git clone https://github.com/your-repo/InterviewPro.git
cd InterviewPro
git pull origin main
```

## 🚀 服务器端部署步骤

### 步骤1: 连接到服务器
使用AWS控制台的"Session Manager"或其他SSH客户端连接到服务器。

### 步骤2: 准备环境
```bash
# 进入项目目录
cd /home/ubuntu/InterviewPro

# 检查Docker环境
docker --version
docker-compose --version

# 如果Docker未安装，执行安装
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    # 重新登录以应用权限
fi

# 如果Docker Compose未安装
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi
```

### 步骤3: 配置环境变量
```bash
# 确保production.env文件存在
ls -la production.env

# 如果不存在，创建它
cat > production.env << 'EOF'
# Flask配置
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this

# 数据库配置
DATABASE_URL=mysql://user:password@mysql:3306/interviewpro

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# CORS配置
CORS_ORIGINS=https://offerott.com,https://www.offerott.com

# Creem.io 正式环境配置
CREEM_TEST_MODE=False
CREEM_API_KEY=creem_6AIW9sH8lsSGaAABHgfdJl
CREEM_BASIC_PRODUCT_ID=prod_7GCAq6iP6E27GOwil4gfDU
CREEM_PREMIUM_PRODUCT_ID=prod_2kqnPDGAScR6Ocf6ujtGi

# 前端配置
FRONTEND_URL=https://offerott.com

# Redis配置
REDIS_URL=redis://redis:6379/0

# DeepSeek API
DEEPSEEK_API_KEY=sk-f33bab4e7cef421e8739c295670cb15c
EOF
```

### 步骤4: 执行部署
```bash
# 停止现有服务
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 清理Docker资源
docker system prune -f

# 构建新镜像
docker-compose -f docker-compose.prod.yml build --no-cache

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
sleep 20

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 步骤5: 验证部署
```bash
# 检查Docker容器状态
docker ps

# 检查后端日志
docker-compose -f docker-compose.prod.yml logs backend | tail -20

# 测试API端点
curl -k https://localhost/api/v1/billing/plans
curl -k https://localhost/api/v1/billing/callback?test=1

# 检查外网访问
curl https://offerott.com/api/v1/billing/plans
curl https://offerott.com/api/v1/billing/callback?test=1
```

## 🔧 故障排除

### 问题1: Docker权限错误
```bash
sudo usermod -aG docker $USER
# 重新登录
```

### 问题2: 端口被占用
```bash
# 查看端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# 停止占用端口的服务
sudo systemctl stop nginx
sudo systemctl stop apache2
```

### 问题3: 内存不足
```bash
# 检查内存使用
free -h
df -h

# 清理系统
sudo apt autoremove
sudo apt autoclean
docker system prune -a
```

### 问题4: SSL证书问题
```bash
# 检查SSL证书
sudo certbot certificates

# 如果需要重新获取证书
sudo certbot --nginx -d offerott.com -d www.offerott.com
```

## ✅ 部署成功标志

部署成功后应该看到：
- ✅ 所有Docker容器状态为"Up"
- ✅ https://offerott.com 可以正常访问
- ✅ https://offerott.com/api/v1/billing/plans 返回JSON数据
- ✅ https://offerott.com/billing 支付页面正常加载

## 📋 部署后配置

### 1. 配置Creem.io Webhook
在Creem.io控制台中设置：
- **Webhook URL**: `https://offerott.com/api/v1/billing/callback`
- **Events**: checkout.completed, payment.completed, payment.failed

### 2. 测试支付流程
1. 访问: https://offerott.com/billing
2. 选择Basic或Premium计划
3. 完成支付
4. 检查回调是否成功

### 3. 监控日志
```bash
# 实时查看回调日志
docker-compose -f docker-compose.prod.yml logs -f backend | grep "PAYMENT CALLBACK"

# 查看错误日志
docker-compose -f docker-compose.prod.yml logs backend | grep -i error
```

## 📞 技术支持

如果部署过程中遇到问题：

1. **检查系统资源**: `free -h` 和 `df -h`
2. **查看Docker日志**: `docker-compose -f docker-compose.prod.yml logs`
3. **检查网络配置**: `curl -I https://offerott.com`
4. **验证环境变量**: `docker-compose -f docker-compose.prod.yml exec backend env | grep CREEM`

## 🎯 预期改善

部署完成后：
- **回调成功率**: 从15-20%提升到95%+
- **API稳定性**: 测试环境 → 生产环境
- **支付体验**: 经常失败 → 稳定可靠
- **网络稳定性**: ngrok不稳定 → 固定域名稳定
