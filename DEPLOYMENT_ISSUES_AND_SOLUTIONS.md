# InterviewPro部署问题和解决方案汇总

## 📋 概述

本文档记录了InterviewPro项目在AWS服务器部署过程中遇到的所有问题和相应的解决方案，用于指导后续部署和问题预防。

## 🚨 主要问题分类

### 1. 服务器资源和环境问题

#### 1.1 旧服务器CPU 100%问题
**问题描述**：
- 旧服务器(3.14.247.189)出现CPU 100%占用
- 服务无响应，SSH连接困难
- 系统资源耗尽导致服务崩溃

**解决方案**：
- 迁移到新AWS服务器(3.138.194.143)
- 采用1核CPU/1GB内存的优化配置
- 实施资源限制策略

**预防措施**：
```yaml
# docker-compose.prod.yml 资源限制配置
services:
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
  backend:
    deploy:
      resources:
        limits:
          memory: 384M
  nginx:
    deploy:
      resources:
        limits:
          memory: 128M
```

#### 1.2 内存不足问题
**问题描述**：
- 1GB内存在运行所有服务时接近极限
- Docker构建过程中可能出现OOM错误

**解决方案**：
- 创建2GB Swap分区
- 实施内存限制和监控
- 优化Docker镜像大小

**预防命令**：
```bash
# 创建Swap分区
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. Python依赖包冲突问题

#### 2.1 numpy/OpenCV兼容性问题
**问题描述**：
```
ImportError: numpy.core.multiarray failed to import
AttributeError: _ARRAY_API not found
```

**根本原因**：
- OpenCV版本与numpy版本不兼容
- 缺少numpy的明确版本指定

**解决方案**：
```txt
# requirements.txt 中添加兼容版本
numpy==1.24.3
opencv-python-headless==4.8.1.78
```

**最佳实践**：
- 始终指定numpy的具体版本
- 使用opencv-python-headless而非opencv-python（无GUI依赖）
- 在本地测试依赖兼容性

#### 2.2 缺失的Python依赖包
**问题描述**：
逐步发现缺失的依赖包：
- `python-dotenv`
- `Flask-JWT-Extended`
- `Flask-Migrate`
- `Flask-SocketIO`
- `Flask-Limiter`
- `marshmallow`
- `openai`
- `PyPDF2`
- `beautifulsoup4`
- `pytesseract`

**解决方案**：
创建完整的requirements.txt：
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
Flask-JWT-Extended==4.5.2
Flask-Migrate==4.0.5
Flask-SocketIO==5.3.4
Flask-Limiter==3.3.1
PyMySQL==1.1.0
redis==5.0.1
Werkzeug==3.0.1
requests==2.31.0
gunicorn==21.2.0
psutil==5.9.0
python-dotenv==1.0.0
marshmallow==3.20.1
openai==1.3.0
PyPDF2==3.0.1
beautifulsoup4==4.12.2
lxml==4.9.3
alembic==1.12.0
bcrypt==4.0.1
cryptography==41.0.5
Pillow==10.0.0
PyJWT==2.8.0
SQLAlchemy==2.0.21
itsdangerous==2.1.2
blinker==1.6.3
click==8.1.7
eventlet==0.33.3
python-multipart==0.0.6
email-validator==2.0.0
pydantic==2.4.0
python-jose==3.3.0
passlib==1.7.4
httpx==0.24.1
aiofiles==23.2.1
jinja2==3.1.2
markupsafe==2.1.3
six==1.16.0
certifi==2023.7.22
charset-normalizer==3.2.0
idna==3.4
urllib3==2.0.4
setuptools==68.2.2
wheel==0.41.2
pip==23.2.1
numpy==1.24.3
opencv-python-headless==4.8.1.78
pytesseract==0.3.10
tesseract==0.1.3
```

**预防措施**：
- 使用`pip freeze > requirements.txt`生成完整依赖列表
- 在开发环境中测试所有功能，确保依赖完整
- 定期更新和维护requirements.txt

### 3. 系统级依赖问题

#### 3.1 OpenCV系统依赖缺失
**问题描述**：
OpenCV需要系统级的图形处理库支持

**解决方案**：
在Dockerfile中添加系统依赖：
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libfontconfig1 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*
```

#### 3.2 Tesseract OCR依赖缺失
**问题描述**：
```
ModuleNotFoundError: No module named 'pytesseract'
```

**解决方案**：
```dockerfile
# 添加Tesseract系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*
```

### 4. Docker配置问题

#### 4.1 Dockerfile CMD语法错误
**问题描述**：
CMD命令格式错误导致容器启动失败

**错误配置**：
```dockerfile
CMD [gunicorn, --bind, 0.0.0.0:5001, ...]
```

**正确配置**：
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "run_complete:app"]
```

#### 4.2 健康检查端点错误
**问题描述**：
健康检查URL不正确导致容器状态异常

**解决方案**：
- 确认健康检查端点存在
- 或者移除健康检查配置

#### 4.3 Docker Compose版本警告
**问题描述**：
```
the attribute `version` is obsolete
```

**解决方案**：
移除docker-compose.yml中的version字段（Docker Compose v2+不再需要）

### 5. 应用启动配置问题

#### 5.1 从run.py切换到run_complete.py
**问题描述**：
- 原使用run.py（简化版，50行）
- 需要切换到run_complete.py（完整版，251行）

**解决方案**：
```dockerfile
ENV FLASK_APP=run_complete.py
CMD ["gunicorn", "run_complete:app", ...]
```

**配置要点**：
- 确保run_complete.py包含所有必要的蓝图注册
- 验证所有API端点正常工作
- 确认应用配置完整

## 🛠️ 部署最佳实践

### 1. 部署前检查清单

```bash
# 1. 检查依赖完整性
pip freeze > requirements_check.txt
diff requirements.txt requirements_check.txt

# 2. 本地Docker测试
docker-compose build
docker-compose up -d
docker-compose logs

# 3. 资源需求评估
docker stats --no-stream

# 4. 应用功能测试
curl http://localhost:8080/
curl http://localhost:8080/api/v1/auth/test
```

### 2. 分阶段部署策略

```bash
# 阶段1：基础服务
docker-compose up -d mysql redis

# 阶段2：应用服务
docker-compose up -d backend

# 阶段3：Web服务
docker-compose up -d nginx

# 验证每个阶段
docker-compose ps
docker-compose logs [service_name]
```

### 3. 资源监控脚本

```bash
#!/bin/bash
# monitor_resources.sh

echo "=== 系统资源监控 ==="
free -h
echo "=== CPU使用率 ==="
top -bn1 | grep 'Cpu(s)'
echo "=== Docker容器资源 ==="
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'
echo "=== 磁盘使用 ==="
df -h
echo "=== Swap使用 ==="
swapon --show
```

### 4. 故障恢复脚本

```bash
#!/bin/bash
# emergency_recovery.sh

echo "开始紧急恢复流程..."

# 停止所有服务
docker-compose down

# 清理Docker缓存
docker system prune -f

# 重新启动服务
docker-compose up -d mysql
sleep 30
docker-compose up -d redis
sleep 10
docker-compose up -d backend
sleep 20
docker-compose up -d nginx

# 检查状态
docker-compose ps
```

## 📚 问题排查流程

### 1. 服务启动失败
```bash
# 检查容器状态
docker-compose ps

# 查看详细日志
docker-compose logs [service_name] --tail=50

# 检查配置文件
docker-compose config

# 检查资源使用
docker stats --no-stream
```

### 2. Python依赖问题
```bash
# 进入容器调试
docker-compose exec backend bash

# 检查Python环境
python --version
pip list

# 测试导入
python -c "import cv2; print('OpenCV OK')"
python -c "import numpy; print('NumPy OK')"
```

### 3. 系统资源问题
```bash
# 检查内存使用
free -h
cat /proc/meminfo

# 检查CPU使用
top -bn1
htop

# 检查磁盘空间
df -h
du -sh /*
```

## 🔄 版本控制和回滚

### 1. 配置文件版本管理
```bash
# 备份重要配置
cp docker-compose.prod.yml docker-compose.prod.yml.backup
cp requirements.txt requirements.txt.backup
cp Dockerfile.prod Dockerfile.prod.backup
```

### 2. 快速回滚方案
```bash
# 回滚到上一个工作版本
docker-compose down
cp docker-compose.prod.yml.backup docker-compose.prod.yml
docker-compose up -d
```

## 📊 性能优化建议

### 1. 内存优化
- 使用alpine镜像减少基础镜像大小
- 设置合理的内存限制
- 优化MySQL配置参数

### 2. 启动时间优化
- 使用多阶段Docker构建
- 预编译Python字节码
- 优化依赖安装顺序

### 3. 监控和告警
- 设置资源使用告警
- 实施健康检查
- 定期备份数据

## 🎯 总结

通过这次部署经历，我们总结出以下关键经验：

1. **完整的依赖管理**：确保requirements.txt包含所有必要依赖
2. **系统级依赖**：OpenCV、Tesseract等需要系统级支持
3. **资源限制**：在小内存服务器上必须严格控制资源使用
4. **分阶段部署**：避免同时启动所有服务造成资源冲突
5. **版本固定**：使用具体版本号避免兼容性问题
6. **监控机制**：实施实时资源监控和告警

遵循这些最佳实践可以显著减少部署问题的发生，提高部署成功率。 