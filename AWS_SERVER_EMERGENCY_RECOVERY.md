# AWS服务器紧急恢复指南

## 当前状况
- **时间**: 2025年7月9日 10:20
- **问题**: 服务器完全无法连接
- **症状**: 
  - SSH连接超时
  - Ping无响应 (100%包丢失)
  - 网站返回502错误

## 诊断结果
根据历史经验，这很可能是**磁盘空间不足**导致的系统完全卡死。

## 紧急恢复步骤

### 1. 检查EC2实例状态
访问AWS控制台 → EC2 → 实例
- 查看实例状态 (running/stopped/stopping)
- 检查实例健康检查状态
- 查看监控图表中的CPU/内存使用情况

### 2. 强制重启实例
如果实例显示运行但无响应：
1. 选择实例 → 操作 → 实例状态 → 重启
2. 如果重启失败，选择"停止"然后"启动"
3. 等待实例完全启动（通常需要2-3分钟）

### 3. 重启后立即清理磁盘空间
```bash
# 测试SSH连接
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'whoami'

# 检查磁盘空间
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'df -h'

# 紧急清理
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 '
sudo docker system prune -a -f
sudo rm -rf /tmp/*
sudo journalctl --vacuum-time=1d
npm cache clean --force 2>/dev/null || echo "npm cache clean 跳过"
'

# 检查清理效果
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'df -h'
```

### 4. 重新启动应用服务
```bash
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 '
cd /home/ubuntu/InterviewPro
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d
'
```

### 5. 验证恢复
```bash
# 检查容器状态
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189 'sudo docker ps'

# 测试网站
curl -I https://offerott.com/
```

## 预防措施

### 1. 设置磁盘空间监控
```bash
# 创建磁盘空间监控脚本
cat > /home/ubuntu/check-disk-space.sh << 'EOF'
#!/bin/bash
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -gt 85 ]; then
    echo "警告: 磁盘使用率 ${USAGE}%"
    docker system prune -f
fi
EOF

# 添加到crontab (每小时检查)
crontab -l | { cat; echo "0 * * * * /home/ubuntu/check-disk-space.sh"; } | crontab -
```

### 2. 定期清理脚本
```bash
# 创建定期清理脚本
cat > /home/ubuntu/cleanup.sh << 'EOF'
#!/bin/bash
echo "$(date): 开始清理"
docker system prune -f
npm cache clean --force 2>/dev/null || true
sudo rm -rf /tmp/*
sudo journalctl --vacuum-time=7d
echo "$(date): 清理完成"
EOF

# 每天凌晨3点执行
crontab -l | { cat; echo "0 3 * * * /home/ubuntu/cleanup.sh >> /var/log/cleanup.log 2>&1"; } | crontab -
```

### 3. 优化Docker镜像
- 使用多阶段构建
- 清理不必要的依赖
- 定期更新基础镜像

## 联系信息
- 服务器IP: 3.14.247.189
- SSH密钥: ~/.ssh/aws-myy-rsa.pem
- 用户名: ubuntu
- 项目路径: /home/ubuntu/InterviewPro

## 备注
根据内存[[memory:2162830]]，当前部署配置：
- 前端容器: interviewpro-frontend-1 (端口80)
- 后端容器: interviewpro-backend-1 (端口5001)  
- Redis容器: interviewpro-redis-1 (端口6379)
- SSL配置: 系统nginx监听443端口 