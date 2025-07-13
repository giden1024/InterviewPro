# AWS InterviewPro 部署步骤

## 🔧 前提条件
- EC2实例运行中且可通过SSH访问
- 安全组配置正确（端口22、80、443、5001开放）
- 有SSH密钥文件

## 📋 部署步骤

### 1. 连接到服务器
```bash
# 替换为您的密钥文件路径
ssh -i /path/to/your-key.pem ubuntu@3.144.27.91

# 如果是Amazon Linux，使用：
# ssh -i /path/to/your-key.pem ec2-user@3.144.27.91
```

### 2. 安装必要软件
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装其他工具
sudo apt-get install -y python3 python3-pip git nginx
```

### 3. 克隆项目代码
```bash
# 克隆您的项目（替换为您的仓库地址）
git clone https://github.com/your-username/InterviewPro.git
cd InterviewPro
```

### 4. 配置环境变量
```bash
# 复制环境配置模板
cp env.production.template .env.production

# 编辑配置文件
nano .env.production
```

**重要配置项：**
```bash
# 数据库（使用SQLite简单部署）
DATABASE_URL=sqlite:///instance/interview.db

# JWT密钥（请生成随机字符串）
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this

# API配置
FLASK_ENV=production
CORS_ORIGINS=http://3.144.27.91,https://your-domain.com

# 前端配置
VITE_API_BASE_URL=http://3.144.27.91/api/v1
```

### 5. 构建和部署
```bash
# 给部署脚本执行权限
chmod +x deploy-aws.sh

# 执行部署
./deploy-aws.sh
```

### 6. 验证部署
```bash
# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 检查健康状态
curl http://localhost/api/v1/health

# 查看日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

### 7. 初始化数据库
```bash
# 创建管理员用户
docker-compose -f docker-compose.prod.yml exec backend python scripts/init_production_db.py
```

## 🌐 访问应用

部署成功后，您可以通过以下方式访问：

- **前端页面**: http://3.144.27.91
- **API接口**: http://3.144.27.91/api/v1
- **健康检查**: http://3.144.27.91/api/v1/health

## 🔒 配置域名和SSL（可选）

如果您有域名，可以配置SSL证书：

```bash
# 配置域名DNS指向您的EC2 IP
# 然后运行SSL配置脚本
./setup-ssl.sh your-domain.com

# 更新环境变量
nano .env.production
# 修改：
# CORS_ORIGINS=https://your-domain.com
# VITE_API_BASE_URL=https://your-domain.com/api/v1

# 重新部署
./deploy-aws.sh
```

## 🚨 故障排除

### 问题1: Docker权限错误
```bash
# 重新登录以应用Docker组权限
exit
ssh -i /path/to/your-key.pem ubuntu@3.144.27.91
```

### 问题2: 端口占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# 停止占用端口的服务
sudo systemctl stop apache2  # 如果有Apache
sudo systemctl stop nginx    # 如果有独立nginx
```

### 问题3: 容器启动失败
```bash
# 查看详细错误日志
docker-compose -f docker-compose.prod.yml logs backend --tail=50
docker-compose -f docker-compose.prod.yml logs frontend --tail=50

# 检查磁盘空间
df -h

# 检查内存使用
free -h
```

## 📞 获取帮助

如果遇到问题，请提供以下信息：
1. 错误日志输出
2. 容器状态：`docker-compose -f docker-compose.prod.yml ps`
3. 系统资源：`df -h && free -h` 