# InterviewPro 部署脚本使用指南

## 📋 脚本概览

本目录包含了InterviewPro项目的完整部署和维护脚本集合，帮助您轻松管理项目部署、监控系统状态以及处理紧急情况。

## 🛠️ 脚本列表

### 1. 部署前检查脚本 (`deploy_checklist.sh`)

**功能**: 部署前的系统环境和配置检查

**使用方法**:
```bash
./scripts/deploy_checklist.sh
```

**检查项目**:
- Docker环境安装情况
- 必要文件完整性
- Python依赖包检查
- 系统资源状况
- 端口占用情况
- Swap配置状态
- Docker配置验证

**输出示例**:
```
🔍 InterviewPro 部署前检查开始...
==================================
1. 检查Docker环境...
✅ Docker已安装
✅ Docker Compose已安装
...
```

### 2. 分阶段部署脚本 (`deploy_staged.sh`)

**功能**: 按阶段有序部署所有服务

**使用方法**:
```bash
./scripts/deploy_staged.sh
```

**部署阶段**:
1. **阶段1**: 启动基础服务 (MySQL + Redis)
2. **阶段2**: 构建并启动Backend服务
3. **阶段3**: 启动Nginx服务

**特性**:
- 自动备份现有配置
- 等待服务完全启动
- 健康检查验证
- 详细的日志输出
- 最终状态验证

### 3. 资源监控脚本 (`monitor_resources.sh`)

**功能**: 实时监控系统和应用状态

**使用方法**:
```bash
# 默认10秒间隔
./scripts/monitor_resources.sh

# 自定义间隔（秒）
./scripts/monitor_resources.sh 30
```

**监控内容**:
- 系统资源使用率 (CPU/内存/磁盘/Swap)
- Docker容器状态
- 网络端口状态
- 应用健康检查
- 最近日志信息
- 资源使用警告

**界面特性**:
- 实时刷新显示
- 颜色编码状态
- 警告阈值提醒
- 按Ctrl+C停止

### 4. 紧急恢复脚本 (`emergency_recovery.sh`)

**功能**: 处理各种紧急情况和故障恢复

**使用方法**:
```bash
# 交互式菜单
./scripts/emergency_recovery.sh

# 直接执行特定功能
./scripts/emergency_recovery.sh status    # 检查状态
./scripts/emergency_recovery.sh restart   # 快速重启
./scripts/emergency_recovery.sh rebuild   # 重建Backend
./scripts/emergency_recovery.sh cleanup   # 清理资源
./scripts/emergency_recovery.sh full      # 完整恢复
```

**恢复选项**:
1. 检查系统状态
2. 快速重启服务
3. 重建Backend服务
4. 清理系统资源
5. 恢复备份配置
6. 创建Swap分区
7. 修复权限问题
8. 完整恢复流程
9. 显示服务状态

## 🚀 快速开始

### 首次部署

```bash
# 1. 部署前检查
./scripts/deploy_checklist.sh

# 2. 如果检查通过，开始部署
./scripts/deploy_staged.sh

# 3. 启动监控
./scripts/monitor_resources.sh
```

### 日常维护

```bash
# 检查系统状态
./scripts/emergency_recovery.sh status

# 监控系统资源
./scripts/monitor_resources.sh 30

# 快速重启服务
./scripts/emergency_recovery.sh restart
```

### 故障处理

```bash
# 进入紧急恢复菜单
./scripts/emergency_recovery.sh

# 或直接执行完整恢复
./scripts/emergency_recovery.sh full
```

## 📊 监控指标说明

### 系统资源警告阈值

| 资源类型 | 警告阈值 | 危险阈值 |
|----------|----------|----------|
| 内存使用率 | 70% | 85% |
| CPU使用率 | 65% | 80% |
| 磁盘使用率 | 75% | 90% |

### 端口状态检查

| 端口 | 服务 | 用途 |
|------|------|------|
| 80 | Nginx | 前端Web服务 |
| 3306 | MySQL | 数据库服务 |
| 6379 | Redis | 缓存服务 |
| 8080 | Backend | API服务 |

## 🔧 故障排查指南

### 常见问题和解决方案

#### 1. 内存不足
**症状**: 容器重启频繁，系统响应慢
**解决**: 
```bash
./scripts/emergency_recovery.sh
# 选择 "6) 创建Swap分区"
```

#### 2. Backend启动失败
**症状**: Backend容器无法正常启动
**解决**:
```bash
./scripts/emergency_recovery.sh rebuild
```

#### 3. 服务全部异常
**症状**: 所有服务都无法访问
**解决**:
```bash
./scripts/emergency_recovery.sh full
```

#### 4. 权限问题
**症状**: 文件无法访问或执行
**解决**:
```bash
./scripts/emergency_recovery.sh
# 选择 "7) 修复权限问题"
```

## 📁 备份和恢复

### 自动备份

部署脚本会自动创建备份：
- 位置: `backups/YYYYMMDD_HHMMSS/`
- 包含: `docker-compose.prod.yml`, `requirements.txt`, `Dockerfile.prod`

### 手动恢复

```bash
./scripts/emergency_recovery.sh
# 选择 "5) 恢复备份配置"
# 然后输入备份目录名称
```

## 🔄 定期维护建议

### 每日检查
```bash
# 快速状态检查
./scripts/emergency_recovery.sh status
```

### 每周维护
```bash
# 清理系统资源
./scripts/emergency_recovery.sh cleanup
```

### 每月维护
```bash
# 完整系统检查
./scripts/deploy_checklist.sh

# 如有问题，执行完整恢复
./scripts/emergency_recovery.sh full
```

## 🚨 紧急情况处理

### CPU 100%
1. 立即停止监控避免更多日志
2. 执行紧急恢复: `./scripts/emergency_recovery.sh restart`
3. 如果无效，执行: `./scripts/emergency_recovery.sh full`

### 内存耗尽
1. 创建Swap: `./scripts/emergency_recovery.sh` → 选择6
2. 清理资源: `./scripts/emergency_recovery.sh cleanup`
3. 重启服务: `./scripts/emergency_recovery.sh restart`

### 磁盘空间不足
1. 清理Docker: `./scripts/emergency_recovery.sh cleanup`
2. 清理日志: `find logs -name "*.log" -mtime +7 -delete`
3. 清理备份: `find backups -mtime +30 -type d -exec rm -rf {} \;`

## 📞 支持和反馈

如果脚本使用过程中遇到问题：

1. 查看脚本日志输出
2. 检查Docker日志: `docker-compose -f docker-compose.prod.yml logs`
3. 运行系统诊断: `./scripts/emergency_recovery.sh status`

## 📝 更新日志

- v1.0.0: 初始版本，包含基础部署和监控功能
- 基于实际部署经验优化的脚本集合
- 包含完整的错误处理和恢复机制

---

**注意**: 所有脚本都需要Docker权限，建议将用户添加到docker用户组或使用sudo执行。 