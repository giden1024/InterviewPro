# InterviewPro 服务器升级迁移方案

## 📋 迁移概述

**当前配置**: t2.micro (1核 + 949MB内存) - IP: 18.219.240.36
**目标配置**: t3.small (2核 + 2GB内存) - 新IP待定
**迁移原因**: 解决内存不足导致的服务器卡死问题

## 🎯 迁移目标

- ✅ 零数据丢失
- ✅ 最小化服务中断时间
- ✅ 完整功能迁移
- ✅ 性能优化配置

---

## 📝 迁移步骤详解

### Phase 1: 准备阶段 (30分钟)

#### 1.1 创建新服务器
```bash
# AWS EC2控制台操作:
1. 启动新实例
   - AMI: Amazon Linux 2023
   - 实例类型: t3.small
   - 存储: 30GB gp3 SSD
   - 安全组: 复制现有安全组(SSH-22, HTTP-80, HTTPS-443)
   - 密钥对: 使用现有的 aws-myy-rsa

2. 记录新服务器IP地址
```

#### 1.2 基础环境配置
```bash
# 连接新服务器
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@<NEW_SERVER_IP>

# 更新系统
sudo yum update -y

# 安装Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录以使docker组生效
exit && ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@<NEW_SERVER_IP>
```

#### 1.3 创建Swap分区 (重要!)
```bash
# 创建2GB swap文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用swap
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 验证swap
free -h
```

### Phase 2: 数据备份阶段 (20分钟)

#### 2.1 从本地推送最新代码
```bash
# 在本地执行
cd /Users/mayuyang/InterviewPro

# 确保代码最新
git add -A
git commit -m "Pre-migration code sync"
git push origin main

# 打包项目
tar -czf interviewpro-migration.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='backend/logs' \
  --exclude='backend/instance' \
  --exclude='.git' \
  .
```

#### 2.2 数据库备份 (如果旧服务器可访问)
```bash
# 尝试备份MySQL数据 (如果服务器恢复)
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@18.219.240.36 \
  "docker exec interviewpro-mysql mysqldump -u root -prootpassword --all-databases" > mysql_backup.sql

# 备份上传文件 (如果有)
scp -i ~/.ssh/aws-myy-rsa.pem -r ec2-user@18.219.240.36:/home/ec2-user/InterviewPro/backend/uploads ./backup_uploads/
```

### Phase 3: 新服务器部署 (45分钟)

#### 3.1 代码部署
```bash
# 上传代码到新服务器
scp -i ~/.ssh/aws-myy-rsa.pem interviewpro-migration.tar.gz ec2-user@<NEW_SERVER_IP>:/home/ec2-user/

# 在新服务器解压
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@<NEW_SERVER_IP>
cd /home/ec2-user
tar -xzf interviewpro-migration.tar.gz
mv InterviewPro InterviewPro_temp 2>/dev/null || true
mkdir -p InterviewPro
mv * InterviewPro/ 2>/dev/null || true
cd InterviewPro
```

#### 3.2 优化配置文件
```bash
# 创建优化的docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: interviewpro-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: interviewpro
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    ports:
      - '3306:3306'
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    command: >
      --default-authentication-plugin=mysql_native_password
      --max_connections=20
      --innodb_buffer_pool_size=128M
      --innodb_log_file_size=32M
      --key_buffer_size=16M
      --tmp_table_size=32M
      --max_heap_table_size=32M

  redis:
    image: redis:alpine
    container_name: interviewpro-redis
    ports:
      - '6379:6379'
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 64M
    command: redis-server --maxmemory 64mb --maxmemory-policy allkeys-lru

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: interviewpro-backend
    ports:
      - '5000:5000'
    environment:
      - DATABASE_URL=mysql+pymysql://user:password@mysql:3306/interviewpro
      - REDIS_URL=redis://redis:6379/0
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    volumes:
      - ./backend:/app
    depends_on:
      - mysql
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  nginx:
    image: nginx:alpine
    container_name: interviewpro-nginx
    ports:
      - '80:80'
    volumes:
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 64M

volumes:
  mysql_data:
EOF
```

#### 3.3 分阶段启动服务
```bash
# 第一阶段：启动数据库
docker-compose up -d mysql redis
sleep 30

# 检查状态
docker ps -a
free -h

# 恢复数据库 (如果有备份)
if [ -f mysql_backup.sql ]; then
  docker exec -i interviewpro-mysql mysql -u root -prootpassword < mysql_backup.sql
fi

# 第二阶段：启动应用
docker-compose up -d backend
sleep 20

# 第三阶段：启动nginx
docker-compose up -d nginx
```

### Phase 4: 测试验证 (20分钟)

#### 4.1 服务状态检查
```bash
# 检查所有容器状态
docker ps -a

# 检查系统资源
free -h
df -h
top -bn1 | head -10

# 检查服务日志
docker-compose logs --tail 20
```

#### 4.2 功能测试
```bash
# 测试MySQL连接
docker exec interviewpro-mysql mysql -u root -prootpassword -e "SHOW DATABASES;"

# 测试Redis连接  
docker exec interviewpro-redis redis-cli ping

# 测试Backend API
curl http://<NEW_SERVER_IP>/api/health

# 测试前端页面
curl -I http://<NEW_SERVER_IP>/
```

#### 4.3 性能测试
```bash
# 创建监控脚本
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    echo "=== $(date) ==="
    free -h | grep Mem
    echo "Load: $(uptime | awk -F'load average:' '{ print $2 }')"
    echo "Docker Status:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo "========================"
    sleep 30
done
EOF

chmod +x monitor.sh
# 在后台运行监控
nohup ./monitor.sh > monitor.log 2>&1 &
```

### Phase 5: 生产切换 (10分钟)

#### 5.1 域名/DNS更新
```bash
# 如果使用域名，更新DNS记录
# 将域名指向新服务器IP: <NEW_SERVER_IP>

# 如果使用AWS Route 53:
# 1. 进入Route 53控制台
# 2. 更新A记录指向新IP
# 3. 设置TTL为60秒以便快速切换
```

#### 5.2 SSL证书配置 (如果需要)
```bash
# 如果使用Let's Encrypt
sudo yum install -y certbot
sudo certbot --nginx -d yourdomain.com

# 或者复制现有证书
scp -i ~/.ssh/aws-myy-rsa.pem -r ec2-user@18.219.240.36:/etc/letsencrypt /tmp/
sudo cp -r /tmp/letsencrypt /etc/
```

### Phase 6: 清理阶段 (15分钟)

#### 6.1 验证新服务器稳定性
```bash
# 运行24小时稳定性测试
# 检查内存泄漏
# 验证所有功能正常
```

#### 6.2 旧服务器清理
```bash
# 确认新服务器运行稳定后
# 在AWS控制台终止旧实例: 18.219.240.36
# 删除关联的EBS卷
# 更新安全组规则
```

---

## 🔧 迁移脚本

### 一键部署脚本
```bash
#!/bin/bash
# deploy-new-server.sh

NEW_SERVER_IP="<待填入新服务器IP>"

echo "=== InterviewPro 新服务器部署脚本 ==="

# 上传代码
echo "上传代码到新服务器..."
scp -i ~/.ssh/aws-myy-rsa.pem interviewpro-migration.tar.gz ec2-user@$NEW_SERVER_IP:/home/ec2-user/

# 执行部署
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@$NEW_SERVER_IP << 'ENDSSH'
cd /home/ec2-user
tar -xzf interviewpro-migration.tar.gz
cd InterviewPro

# 创建swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 分阶段启动
echo "启动数据库服务..."
docker-compose up -d mysql redis
sleep 30

echo "启动应用服务..."
docker-compose up -d backend
sleep 20

echo "启动Web服务..."
docker-compose up -d nginx

echo "部署完成！"
docker ps -a
free -h
ENDSSH

echo "=== 部署完成，请访问 http://$NEW_SERVER_IP 测试 ==="
```

---

## ⚠️ 风险控制

### 回滚计划
如果新服务器出现问题：
1. 立即停止新服务器的服务
2. 恢复DNS指向原服务器（如果还能访问）
3. 使用备份数据重新部署

### 监控告警
```bash
# 内存使用率监控
watch -n 5 'free -h | grep Mem | awk "{print \$3/\$2*100}"'

# 如果内存使用率 > 85%，立即告警
```

---

## 📋 迁移检查清单

### 迁移前检查
- [ ] 新服务器创建完成
- [ ] SSH密钥配置正确
- [ ] 安全组配置复制
- [ ] 本地代码已提交并推送

### 迁移中检查  
- [ ] Docker安装成功
- [ ] Swap分区创建
- [ ] 代码上传完整
- [ ] 容器分阶段启动
- [ ] 每个阶段资源检查

### 迁移后验证
- [ ] 所有容器运行正常
- [ ] API接口响应正常
- [ ] 前端页面加载正常
- [ ] 数据库连接正常
- [ ] 内存使用率 < 80%
- [ ] 系统负载正常

---

## 💰 成本对比

| 项目 | 旧配置(t2.micro) | 新配置(t3.small) | 差异 |
|------|------------------|------------------|------|
| 月费用 | ~$8.5 | ~$16.8 | +$8.3 |
| CPU | 1核 | 2核 | +100% |
| 内存 | 1GB | 2GB | +100% |
| 稳定性 | 经常卡死 | 稳定运行 | 显著提升 |

**投资回报**：每月多投入$8.3，获得稳定的服务和更好的用户体验

---

## 📞 联系支持

如果迁移过程中遇到问题：
1. 检查monitor.log日志
2. 运行docker-compose logs查看详细日志  
3. 使用回滚计划恢复服务

**预计总迁移时间**: 2-3小时
**服务中断时间**: < 10分钟（DNS切换时间） 