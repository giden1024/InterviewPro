# InterviewPro 综合部署问题指南

## 📋 概述

本文档汇总了 InterviewPro 项目在多次部署过程中遇到的所有问题、解决方案和预防措施，旨在为后续部署提供完整的参考指南。

**最后更新**: 2025年8月3日  
**涵盖问题**: 从初期部署到最新数据库结构同步的所有问题  

---

## 🚨 问题分类与优先级

### 🔴 **严重问题 (P0)** - 导致服务完全不可用
1. [数据库表结构不一致](#1-数据库表结构不一致问题)
2. [CPU 100% 占用](#2-cpu-100-占用问题)
3. [关键依赖包缺失](#3-python依赖包问题)

### 🟡 **重要问题 (P1)** - 影响核心功能
4. [文件上传解析失败](#4-文件上传和解析问题)
5. [Docker 构建失败](#5-docker配置问题)
6. [SSL 证书问题](#6-ssl和网络配置问题)

### 🟢 **一般问题 (P2)** - 影响用户体验
7. [代码版本不一致](#7-代码版本控制问题)
8. [资源配置不当](#8-服务器资源配置问题)

---

## 🔴 严重问题详解

### 1. 数据库表结构不一致问题

#### 📝 问题描述
**最新发现的关键问题** - 本地开发环境和远程生产环境的数据库表结构存在显著差异，导致 API 调用失败。

**典型错误信息**:
```sql
Unknown column 'resumes.original_filename' in 'field list'
Unknown column 'jobs.responsibilities' in 'field list'
'processed' is not among the defined enum values
```

#### 🔍 根本原因
1. **表结构版本不同步**: 
   - 本地数据库: `dev_interview_genius` (完整表结构)
   - 远程数据库: `interviewpro` (旧版本表结构)

2. **枚举值不匹配**:
   - 本地: `ENUM('UPLOADED','PROCESSING','PROCESSED','FAILED')`
   - 远程: `enum('uploaded','processing','processed','failed')`

3. **字段类型差异**:
   - `projects` 字段: 本地为 `text`，远程为 `json`
   - `avatar_url` 字段: 本地为 `varchar(255)`，远程为 `text`

#### ✅ 解决方案
```bash
# 1. 备份远程数据库
mysqldump -u root -p interviewpro > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 导出本地表结构
mysqldump -u root --no-data dev_interview_genius > local_schema.sql

# 3. 重新创建远程数据库
DROP DATABASE interviewpro;
CREATE DATABASE interviewpro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 4. 导入新表结构并迁移数据
mysql -u root -p interviewpro < local_schema.sql
```

#### 🛡️ 预防措施
1. **建立数据库版本控制**:
   ```bash
   # 使用 Flask-Migrate 管理数据库版本
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

2. **定期结构对比检查**:
   ```bash
   # 创建结构对比脚本
   ./scripts/compare_db_schemas.sh
   ```

3. **统一开发环境**:
   - 本地和生产环境使用相同的数据库引擎 (MySQL)
   - 使用相同的字符集和排序规则
   - 定期同步表结构定义

### 2. CPU 100% 占用问题

#### 📝 问题描述
部署完成后服务器 CPU 占用率达到 100%，导致系统无响应、SSH 连接困难、网站无法访问。

#### 🔍 根本原因
1. **Docker 容器无资源限制**: 容器可以无限制使用系统资源
2. **应用程序死循环**: 后端代码存在无限循环或重试机制
3. **内存不足导致频繁 Swap**: 1GB 内存不足以支撑所有服务
4. **数据库连接问题**: 连接池配置不当，重复连接尝试

#### ✅ 解决方案
1. **添加 Docker 资源限制**:
   ```yaml
   # docker-compose.prod.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '0.8'
             memory: 384M
           reservations:
             cpus: '0.2'
             memory: 128M
     mysql:
       deploy:
         resources:
           limits:
             memory: 512M
     redis:
       deploy:
         resources:
           limits:
             memory: 64M
   ```

2. **创建 Swap 分区**:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

3. **优化应用配置**:
   ```python
   # 数据库连接池配置
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_size': 5,
       'pool_recycle': 3600,
       'pool_pre_ping': True,
       'max_overflow': 10
   }
   ```

### 3. Python依赖包问题

#### 📝 问题描述
Docker 构建过程中出现各种依赖包缺失或版本冲突问题。

**典型错误**:
```
ImportError: numpy.core.multiarray failed to import
ModuleNotFoundError: No module named 'Flask-Limiter'
AttributeError: _ARRAY_API not found
```

#### 🔍 根本原因
1. **numpy/OpenCV 版本不兼容**
2. **requirements.txt 不完整**
3. **系统级依赖缺失**

#### ✅ 解决方案
1. **固定关键依赖版本**:
   ```txt
   # requirements.txt 关键版本
   numpy==1.24.3
   opencv-python-headless==4.8.1.78
   Flask-Limiter==3.5.0
   celery==5.3.4
   ```

2. **完整的系统依赖**:
   ```dockerfile
   # Dockerfile.prod
   RUN apt-get update && apt-get install -y \
       gcc g++ curl \
       libgl1-mesa-glx libglib2.0-0 libsm6 \
       libxext6 libxrender-dev libgomp1 \
       portaudio19-dev python3-dev libasound2-dev \
       tesseract-ocr tesseract-ocr-eng \
       && rm -rf /var/lib/apt/lists/*
   ```

---

## 🟡 重要问题详解

### 4. 文件上传和解析问题

#### 📝 问题描述
中文文件名的简历上传后解析失败，`file_type` 字段为空。

#### 🔍 根本原因
`secure_filename('陈熙蕾.docx')` 返回 `'docx'`，导致文件扩展名提取失败。

#### ✅ 解决方案
```python
# 修复文件扩展名提取逻辑
file_extension = get_file_extension(file.filename)  # 从原始文件名获取
filename = f"{uuid.uuid4().hex}.{file_extension}"
original_filename = secure_filename(file.filename)
```

### 5. Docker配置问题

#### 📝 问题描述
1. CMD 命令 JSON 格式错误
2. 健康检查端点不存在
3. Docker Compose 版本警告

#### ✅ 解决方案
```dockerfile
# 正确的 CMD 格式
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "run_complete:app"]

# 移除或修复健康检查
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:5001/api/v1/health || exit 1
```

### 6. SSL和网络配置问题

#### 📝 问题描述
HTTPS 证书配置、域名解析、Nginx 反向代理配置问题。

#### ✅ 解决方案
```nginx
# nginx.conf
server {
    listen 80;
    server_name offerott.com www.offerott.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name offerott.com www.offerott.com;
    
    ssl_certificate /etc/letsencrypt/live/offerott.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/offerott.com/privkey.pem;
    
    location /api/ {
        proxy_pass http://backend:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🟢 一般问题详解

### 7. 代码版本控制问题

#### 📝 问题描述
本地代码与服务器代码不一致，导致功能差异和部署问题。

#### ✅ 解决方案
```bash
# 建立统一的部署流程
git add .
git commit -m "Deploy: sync all changes"
git push origin main

# 服务器端同步
ssh server "cd /path/to/project && git pull && docker-compose restart"
```

### 8. 服务器资源配置问题

#### 📝 问题描述
1GB 内存的 EC2 实例资源不足，频繁出现 OOM 错误。

#### ✅ 解决方案
1. **资源监控脚本**:
   ```bash
   #!/bin/bash
   # monitor_resources.sh
   while true; do
       echo "=== $(date) ==="
       free -h
       docker stats --no-stream
       sleep 30
   done
   ```

2. **服务启动顺序优化**:
   ```yaml
   services:
     mysql:
       restart: unless-stopped
     redis:
       depends_on:
         - mysql
     backend:
       depends_on:
         - mysql
         - redis
   ```

---

## 🛠️ 完整部署检查清单

### 部署前检查 (Pre-deployment)
- [ ] 本地功能完整测试
- [ ] 数据库表结构对比检查
- [ ] requirements.txt 完整性验证
- [ ] Docker 本地构建测试
- [ ] 代码版本同步确认

### 部署中监控 (During deployment)
- [ ] 实时资源使用监控
- [ ] Docker 构建日志检查
- [ ] 服务启动顺序确认
- [ ] 健康检查端点验证

### 部署后验证 (Post-deployment)
- [ ] 所有 API 端点测试
- [ ] 数据库连接验证
- [ ] 文件上传功能测试
- [ ] SSL 证书状态检查
- [ ] 性能指标监控

---

## 📊 部署脚本模板

### 1. 全面部署脚本
```bash
#!/bin/bash
# deploy_comprehensive.sh

set -e

echo "🚀 开始综合部署流程..."

# 1. 环境检查
echo "📋 检查部署环境..."
./scripts/check_deployment_environment.sh

# 2. 代码同步
echo "🔄 同步代码..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || true
git push origin main

# 3. 服务器部署
echo "🌐 部署到服务器..."
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 << 'EOF'
    cd /home/ec2-user/InterviewPro
    git pull
    docker-compose -f docker-compose.prod.yml down
    docker system prune -f
    docker-compose -f docker-compose.prod.yml build --no-cache
    docker-compose -f docker-compose.prod.yml up -d
EOF

# 4. 部署验证
echo "✅ 验证部署结果..."
sleep 30
./scripts/verify_deployment.sh

echo "🎉 部署完成！"
```

### 2. 数据库结构同步脚本
```bash
#!/bin/bash
# sync_database_schema.sh

echo "🔄 开始数据库结构同步..."

# 备份远程数据库
ssh server "docker exec mysql mysqldump -u root -p interviewpro > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql"

# 导出本地结构
mysqldump -u root --no-data dev_interview_genius > /tmp/local_schema.sql

# 传输并应用
scp /tmp/local_schema.sql server:/tmp/
ssh server "docker exec -i mysql mysql -u root -p interviewpro < /tmp/local_schema.sql"

echo "✅ 数据库结构同步完成"
```

---

## 🎯 最佳实践总结

### 1. 开发阶段
- 使用与生产环境一致的数据库 (MySQL)
- 定期更新 requirements.txt
- 本地 Docker 环境测试
- 代码提交前的完整功能测试

### 2. 部署阶段
- 分阶段部署 (数据库 → 后端 → 前端)
- 实时监控资源使用情况
- 保持部署日志的完整记录
- 准备快速回滚方案

### 3. 运维阶段
- 定期数据库结构对比
- 资源使用情况监控
- 定期安全更新
- 日志轮转和清理

### 4. 应急响应
- CPU 100% 时的快速诊断脚本
- 数据库连接问题的排查步骤
- 服务快速重启的标准流程
- 紧急回滚的操作指南

---

## 📞 快速问题定位

### 常见错误快速定位表

| 错误类型 | 关键词 | 快速检查命令 | 解决方案 |
|---------|--------|-------------|----------|
| 数据库表不存在 | `Table doesn't exist` | `SHOW TABLES;` | 运行数据库迁移 |
| 字段不存在 | `Unknown column` | `DESCRIBE table_name;` | 同步表结构 |
| 依赖包缺失 | `ModuleNotFoundError` | `pip list \| grep package` | 更新 requirements.txt |
| CPU 100% | `load average` | `htop`, `docker stats` | 添加资源限制 |
| 内存不足 | `OOMKilled` | `free -h`, `dmesg` | 创建 Swap 分区 |
| 端口占用 | `Address already in use` | `lsof -i :port` | 停止冲突进程 |

---

## 🔚 结语

这份指南汇总了 InterviewPro 项目部署过程中遇到的所有重要问题。随着项目的发展，应该持续更新这份文档，记录新的问题和解决方案。

**记住**: 每次部署前都要回顾这份检查清单，可以避免 90% 的常见问题！

**最后更新**: 2025年8月3日  
**下次更新**: 根据新问题及时更新 