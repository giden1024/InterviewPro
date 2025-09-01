# 🚀 InterviewPro 轻量化部署指南

## 📋 部署方式对比

| 部署方式 | 时间 | 适用场景 | 命令 |
|---------|------|----------|------|
| **🔥 热更新** | 30秒 | 纯代码逻辑修改 | `./scripts/deploy_hot_update.sh` |
| **🎨 前端专用** | 1分钟 | 仅前端修改 | `./scripts/deploy_frontend_only.sh` |
| **🔄 服务重启** | 2-3分钟 | 配置文件修改 | `./scripts/deploy_restart.sh` |
| **🧠 智能检测** | 自动选择 | 自动判断最优方案 | `./scripts/deploy_smart.sh` |
| **🏗️  完整重构建** | 10-15分钟 | 依赖包/数据库修改 | `./scripts/deploy_full_rebuild.sh` |

---

## 🎯 推荐使用方式

### 🥇 **首选：智能部署**
```bash
./scripts/deploy_smart.sh
```
- 自动检测修改内容
- 自动选择最优部署方式
- 无需手动判断

### 🥈 **手动选择场景**

#### 1. 修改了 React 组件、页面、样式
```bash
./scripts/deploy_frontend_only.sh
```
**示例场景**：
- 修改了 `HomePage.tsx`
- 更新了 CSS 样式
- 修改了前端路由

#### 2. 修改了 Python 业务逻辑
```bash
./scripts/deploy_hot_update.sh
```
**示例场景**：
- 修改了 API 接口逻辑
- 更新了业务处理函数
- 修改了数据库查询逻辑

#### 3. 修改了配置文件
```bash
./scripts/deploy_restart.sh
```
**示例场景**：
- 修改了环境变量
- 更新了 Docker Compose 配置
- 修改了 Nginx 配置

#### 4. 修改了依赖包或数据库
```bash
./scripts/deploy_full_rebuild.sh
```
**示例场景**：
- 更新了 `requirements.txt`
- 修改了 `package.json`
- 更新了数据库模型

---

## ⚡ 极速部署技巧

### 1. **开发时保持服务运行**
```bash
# 本地开发时，保持这些服务在后台运行
cd backend && source venv/bin/activate && python run_complete.py &
cd frontend && npm run dev &
```

### 2. **使用文件监控自动部署**
```bash
# 安装文件监控工具 (可选)
brew install fswatch  # macOS
# sudo apt-get install inotify-tools  # Linux

# 监控文件变化自动部署
fswatch -o backend/app frontend/src | xargs -n1 -I{} ./scripts/deploy_smart.sh
```

### 3. **批量修改一次性部署**
```bash
# 避免每个小修改都部署，积累一批修改后一次性部署
git add .
git stash  # 暂存修改
# ... 继续开发其他功能 ...
git stash pop  # 恢复修改
./scripts/deploy_smart.sh  # 一次性部署所有修改
```

---

## 🛠️ 部署脚本详解

### 热更新原理
```bash
# 直接复制代码到运行中的容器
docker cp backend/app/. interviewpro-backend:/app/app/
docker exec interviewpro-backend pkill -HUP gunicorn  # 重载进程
```

### 前端更新原理
```bash
# 本地构建 + 直接替换静态文件
npm run build
docker cp dist/. interviewpro-nginx:/usr/share/nginx/html/
```

### 智能检测逻辑
```bash
# 检测修改文件类型
if 修改了依赖包 -> 完整重构建
elif 仅修改前端 -> 前端专用部署
elif 仅修改后端代码 -> 热更新
else -> 服务重启
```

---

## 🚨 注意事项

### ✅ **安全使用**
1. **生产环境谨慎使用热更新**
   - 热更新跳过了一些安全检查
   - 建议先在测试环境验证

2. **重要修改使用完整重构建**
   - 数据库模型修改
   - 关键依赖包更新
   - 安全相关修改

### ⚠️ **故障恢复**
```bash
# 如果热更新出现问题，快速回滚
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 \
  'cd /home/ec2-user/InterviewPro && docker-compose -f docker-compose.prod.yml restart backend'

# 如果问题严重，使用完整重构建
./scripts/deploy_full_rebuild.sh
```

### 🔍 **部署验证**
每次部署后都会自动验证：
```bash
# 后端健康检查
curl -s https://offerott.com/api/v1/health

# 前端可访问性检查
curl -s https://offerott.com/

# 服务状态检查
docker-compose ps
```

---

## 📊 性能对比

### 传统 Docker Compose 部署
```
停止服务 (30s) → 构建镜像 (5-10min) → 启动服务 (30s) → 验证 (30s)
总计: 6-11分钟
```

### 轻量化部署
```
热更新: 代码同步 (10s) → 进程重载 (5s) → 验证 (15s) = 30秒
前端专用: 构建 (30s) → 上传 (15s) → 替换 (5s) → 验证 (10s) = 1分钟
服务重启: 同步 (15s) → 重启 (60s) → 验证 (30s) = 2分钟
```

**性能提升**: 10-20倍 🚀

---

## 🎯 最佳实践

### 开发流程建议
1. **小修改** → 使用智能部署 `./scripts/deploy_smart.sh`
2. **功能完成** → 本地测试 → 智能部署
3. **版本发布** → 完整测试 → 完整重构建部署
4. **紧急修复** → 热更新 → 后续完整重构建验证

### 团队协作
```bash
# 团队成员统一使用智能部署
alias deploy='./scripts/deploy_smart.sh'

# 在 .bashrc 或 .zshrc 中添加
echo "alias deploy='./scripts/deploy_smart.sh'" >> ~/.zshrc
```

---

## 🔚 总结

通过这套轻量化部署方案，你可以：

- **🚀 部署速度提升 10-20倍**
- **⚡ 开发效率大幅提升**
- **🎯 根据修改类型智能选择部署方式**
- **🛡️ 保持生产环境稳定性**

**记住**：大部分日常修改都可以使用 `./scripts/deploy_smart.sh`，它会自动选择最优的部署方式！

---

*最后更新: 2025年8月3日*  
*建议: 收藏这个指南，每次部署前参考使用* 