# InterviewPro 部署经验总结

## 🎯 核心问题与解决方案

### 1. 🔴 **数据库表结构不一致** (最关键问题)

**问题**: 本地和远程数据库表结构不同步，导致 API 500 错误
```
Unknown column 'resumes.original_filename' in 'field list'
'processed' is not among the defined enum values
```

**解决**: 
- 备份远程数据 → 导出本地表结构 → 重建远程数据库 → 迁移数据
- **预防**: 使用 Flask-Migrate，定期对比表结构

### 2. 🔴 **CPU 100% 占用**

**问题**: 部署后服务器 CPU 满载，系统无响应
**解决**: 
- 添加 Docker 资源限制 (CPU: 0.8, 内存: 384M)
- 创建 2GB Swap 分区
- 优化数据库连接池配置

### 3. 🟡 **依赖包冲突**

**问题**: numpy/OpenCV 版本不兼容，系统依赖缺失
**解决**: 
- 固定版本: `numpy==1.24.3`, `opencv-python-headless==4.8.1.78`
- 添加系统依赖: tesseract-ocr, libgl1-mesa-glx 等

### 4. 🟡 **文件上传失败**

**问题**: 中文文件名处理错误，`file_type` 为空
**解决**: 从原始文件名提取扩展名，而非 secure_filename 结果

---

## ⚡ 部署前必查清单

### 📋 **环境检查**
- [ ] 本地和远程数据库表结构一致性
- [ ] requirements.txt 完整性 (特别是 numpy, Flask-Limiter, celery)
- [ ] Docker 资源限制配置
- [ ] Swap 分区创建 (2GB)

### 🔧 **代码同步**
- [ ] 所有本地修改已提交到 Git
- [ ] 远程服务器代码已更新到最新版本
- [ ] 文件权限和路径正确

### 🚀 **部署流程**
1. **分阶段部署**: MySQL → Redis → Backend → Nginx
2. **实时监控**: `docker stats`, `free -h`, `htop`
3. **日志检查**: `docker-compose logs --tail=50 backend`
4. **功能验证**: 登录、上传、API 测试

---

## 🚨 应急处理

### CPU 100% 紧急处理
```bash
# 1. 立即检查资源使用
docker stats --no-stream
htop

# 2. 重启服务 (如果 SSH 还能连接)
docker-compose -f docker-compose.prod.yml restart backend

# 3. 强制重启 (如果系统无响应)
# 通过 AWS 控制台重启实例
```

### 数据库问题快速诊断
```bash
# 检查表是否存在
docker exec mysql mysql -u root -p interviewpro -e "SHOW TABLES;"

# 检查表结构
docker exec mysql mysql -u root -p interviewpro -e "DESCRIBE resumes;"

# 检查枚举值
docker exec mysql mysql -u root -p interviewpro -e "SHOW COLUMNS FROM resumes WHERE Field = 'status';"
```

---

## 📊 关键配置模板

### Docker 资源限制
```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.8'
          memory: 384M
  mysql:
    deploy:
      resources:
        limits:
          memory: 512M
```

### 系统依赖 (Dockerfile)
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc g++ curl \
    libgl1-mesa-glx libglib2.0-0 libsm6 \
    libxext6 libxrender-dev libgomp1 \
    tesseract-ocr tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*
```

### 关键依赖版本
```txt
numpy==1.24.3
opencv-python-headless==4.8.1.78
Flask-Limiter==3.5.0
celery==5.3.4
```

---

## 🎯 部署成功率提升方案

### 本地预检 (90% 问题可提前发现)
1. **Docker 本地构建测试**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   docker-compose logs
   ```

2. **数据库结构对比**
   ```bash
   # 导出本地结构
   mysqldump -u root --no-data dev_interview_genius > local_schema.sql
   
   # 对比远程结构
   ssh server "docker exec mysql mysqldump -u root -p --no-data interviewpro" > remote_schema.sql
   diff local_schema.sql remote_schema.sql
   ```

3. **依赖完整性检查**
   ```bash
   pip freeze > current_requirements.txt
   diff requirements.txt current_requirements.txt
   ```

### 监控部署过程
```bash
# 实时监控脚本
#!/bin/bash
while true; do
    echo "=== $(date) ==="
    echo "CPU/Memory:"
    free -h | head -2
    echo "Docker Status:"
    docker-compose ps
    echo "Backend Logs (last 3 lines):"
    docker-compose logs --tail=3 backend
    echo "---"
    sleep 30
done
```

---

## 💡 经验教训

### ✅ **成功经验**
1. **分阶段部署**降低了失败风险
2. **资源限制**避免了系统崩溃
3. **实时监控**能及时发现问题
4. **数据库结构同步**解决了大部分 API 错误

### ❌ **失败教训**
1. **忽视本地/远程环境差异**导致反复部署失败
2. **缺乏资源限制**造成系统资源耗尽
3. **依赖版本不固定**引发不可预期的兼容性问题
4. **缺少部署前检查**浪费大量调试时间

### 🔮 **改进方向**
1. 建立 CI/CD 流水线自动化部署
2. 使用 Docker 多阶段构建优化镜像大小
3. 实施数据库版本控制 (Flask-Migrate)
4. 增加自动化测试覆盖部署流程

---

## 📞 快速联系

**遇到问题时的处理顺序**:
1. 查看这份文档的对应章节
2. 检查 `docker-compose logs` 错误信息
3. 运行相应的诊断命令
4. 如果问题未在文档中，记录并更新文档

**记住**: 每次成功解决新问题后，都要更新这份文档！

---

*最后更新: 2025年8月3日*  
*下次更新: 遇到新问题时及时更新* 