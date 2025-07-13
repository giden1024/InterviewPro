# Docker修复手动操作指令

## 🔧 立即执行以下命令

### 1️⃣ SSH连接到服务器
```bash
ssh -i ~/.ssh/aws-myy-rsa.pem ubuntu@3.14.247.189
```

### 2️⃣ 进入项目目录
```bash
cd /home/ubuntu/InterviewPro
```

### 3️⃣ 检查问题文件
```bash
sed -n '83p' requirements.txt | cat -A
```

### 4️⃣ 修复第83行格式错误
```bash
sed -i '83s/.*/soundfile==0.12.1/' requirements.txt
```

### 5️⃣ 验证修复
```bash
sed -n '83p' requirements.txt
```

### 6️⃣ 清理Docker缓存
```bash
sudo docker system prune -a -f
```

### 7️⃣ 重启Docker服务
```bash
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up --build -d
```

### 8️⃣ 监控启动过程
```bash
# 查看容器状态
sudo docker ps

# 查看日志
sudo docker-compose -f docker-compose.prod.yml logs --tail=20

# 监控构建进度（如果还在构建中）
sudo docker-compose -f docker-compose.prod.yml logs -f
```

### 9️⃣ 测试网站
退出SSH并在本地测试：
```bash
curl -I https://offerott.com/home
```

## ⚠️ 预期结果
- Docker构建应该成功完成
- 3个容器应该运行：interviewpro-backend-1, interviewpro-frontend-1, interviewpro-redis-1
- 端口80应该开放
- 网站应该返回200状态码

## 🆘 如果仍然失败
检查具体错误消息：
```bash
sudo docker-compose -f docker-compose.prod.yml logs backend
``` 