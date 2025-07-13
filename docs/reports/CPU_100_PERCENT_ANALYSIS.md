# InterviewPro 部署后CPU 100%问题分析报告

**问题描述**: 每次部署完成后，服务器CPU占用接近100%，导致502错误和SSH无法连接

## 🔍 **问题根本原因分析**

### 1. **Docker容器资源问题**（最可能）
- ✅ **无限循环/死循环**: 后端应用可能存在代码死循环
- ✅ **内存泄漏**: 应用程序内存使用不断增长，触发频繁GC
- ✅ **容器没有资源限制**: Docker容器可以无限制使用系统资源
- ✅ **多个容器同时启动**: 部署时新老容器同时运行

### 2. **应用程序层面问题**
- ✅ **数据库连接问题**: 
  - 连接池配置不当
  - 数据库连接泄漏
  - 重复连接尝试
- ✅ **AI服务调用问题**:
  - OpenAI API调用异常
  - 无限重试机制
  - 大量并发AI请求
- ✅ **日志系统问题**: 过量日志写入磁盘

### 3. **系统资源配置问题**
- ✅ **EC2实例规格不足**: t2.micro/small无法承载应用负载
- ✅ **内存不足**: 导致频繁swap，CPU使用率飙升
- ✅ **磁盘IO瓶颈**: 日志、数据库写入过频繁

### 4. **部署流程问题**
- ✅ **优雅关闭缺失**: 旧容器没有正确停止
- ✅ **服务启动顺序**: 后端在数据库启动前就开始重试连接
- ✅ **缓存问题**: 重复构建或下载导致资源消耗

## 🚨 **问题影响链**

```
部署触发 → 容器启动 → 应用问题触发 → CPU 100% → 系统无响应 → SSH/Web无法访问
```

## 🔧 **立即解决方案**

### 方案1: 添加Docker资源限制
```yaml
# docker-compose.yml 修改
services:
  backend:
    # 限制CPU和内存使用
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 方案2: 优化启动顺序和健康检查
```yaml
services:
  backend:
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 方案3: 修复应用程序问题
```python
# 后端代码修改建议

# 1. 数据库连接池配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 5,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 10
}

# 2. 添加重试限制
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def ai_service_call():
    # AI服务调用
    pass

# 3. 优化日志配置
import logging
logging.getLogger().setLevel(logging.WARNING)
```

## 🛠️ **监控和诊断工具**

### 创建资源监控脚本
```bash
#!/bin/bash
# monitor-resources.sh
while true; do
    echo "=== $(date) ==="
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
    echo "Memory: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
    echo "Docker containers:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo "Top processes:"
    ps aux --sort=-%cpu | head -5
    echo "---"
    sleep 30
done
```

## 🎯 **系统优化建议**

### 1. **升级EC2实例**
- 当前可能使用: t2.micro (1 vCPU, 1GB RAM)
- 建议升级到: t3.medium (2 vCPU, 4GB RAM) 或更高

### 2. **优化Docker配置**
```yaml
# 添加到 docker-compose.yml
version: '3.8'
services:
  backend:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    environment:
      - FLASK_ENV=production
      - WORKERS=2  # 限制worker数量
```

### 3. **添加系统级监控**
```bash
# 安装系统监控
sudo apt update
sudo apt install htop iotop nethogs -y

# 设置自动重启机制
echo "*/5 * * * * if [ \$(ps aux | awk '{sum += \$3} END {print sum}') -gt 90 ]; then docker-compose restart; fi" | crontab -
```

## 🚀 **紧急修复计划**

### 立即执行（通过AWS控制台）:
1. **检查实例类型和资源**
2. **通过控制台连接服务器**
3. **执行资源清理**:
   ```bash
   # 停止所有Docker服务
   docker-compose down
   # 清理系统
   docker system prune -f
   # 检查资源使用
   top
   htop
   ```

### 修改部署脚本:
1. **添加资源检查**
2. **优雅停止服务**
3. **分步启动服务**
4. **资源监控**

## 📊 **预防措施**

1. **部署前检查**: CPU/内存使用率
2. **分阶段部署**: 逐个启动服务
3. **健康检查**: 确保服务正常后再继续
4. **自动回滚**: 检测到资源异常时自动回滚
5. **监控告警**: CPU超过80%时发送告警

---

**结论**: 这是一个典型的资源管理和应用优化问题，需要从Docker配置、应用代码、系统资源三个层面同时解决。 