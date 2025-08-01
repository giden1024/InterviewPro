#!/bin/bash

echo "🔧 手动更新AWS服务器代码"
echo "========================"

# 设置变量
SERVER_IP="3.138.194.143"
SERVER_USER="ec2-user"

echo "📦 第一步: 打包本地代码"
# 创建代码压缩包
tar -czf InterviewPro-latest.tar.gz \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='instance' \
    --exclude='logs' \
    --exclude='uploads' \
    --exclude='temp' \
    --exclude='*.tar.gz' \
    .

echo "✅ 代码打包完成"

echo ""
echo "📤 第二步: 上传到AWS服务器"
# 上传代码到服务器（注意：这需要SSH密钥配置正确）
# 由于SSH连接问题，我们使用scp的替代方案

echo "⚠️  由于SSH密钥问题，建议手动执行以下步骤："
echo ""
echo "1. 将 InterviewPro-latest.tar.gz 文件上传到 AWS 服务器"
echo "2. 在服务器上执行以下命令："
echo ""
echo "# 备份现有代码"
echo "sudo cp -r /home/ec2-user/InterviewPro /home/ec2-user/InterviewPro-backup-$(date +%Y%m%d)"
echo ""
echo "# 解压新代码"
echo "cd /home/ec2-user"
echo "tar -xzf InterviewPro-latest.tar.gz -C InterviewPro --strip-components=1"
echo ""
echo "# 重启服务"
echo "cd /home/ec2-user/InterviewPro"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "# 检查服务状态"
echo "docker-compose -f docker-compose.prod.yml ps"

echo ""
echo "🏗️  第三步: 自动生成部署命令脚本"

cat > aws_server_update_commands.sh << 'EOF'
#!/bin/bash
# 在AWS服务器上执行此脚本

echo "🔄 更新InterviewPro服务器代码"
echo "==========================="

# 切换到项目目录
cd /home/ec2-user/InterviewPro

echo "🛑 停止现有服务"
docker-compose -f docker-compose.prod.yml down

echo "🗑️  清理Docker缓存"
docker system prune -f
docker image prune -f

echo "🔄 拉取最新代码"
git pull origin main

echo "🏗️  重建并启动服务"
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate

echo "⏳ 等待服务启动"
sleep 30

echo "📊 检查服务状态"
docker-compose -f docker-compose.prod.yml ps

echo "🧪 测试API健康状态"
curl -s https://offerott.com/health | jq .

echo "✅ 部署完成"
EOF

chmod +x aws_server_update_commands.sh

echo ""
echo "📋 生成的文件:"
echo "- InterviewPro-latest.tar.gz (代码压缩包)"
echo "- aws_server_update_commands.sh (服务器执行脚本)"
echo ""
echo "🚀 推荐执行方案:"
echo "1. 通过AWS控制台或其他方式连接到服务器"
echo "2. 在服务器上执行: git pull origin main"
echo "3. 然后执行: docker-compose -f docker-compose.prod.yml up -d --build --force-recreate"
echo ""
echo "📞 或者直接通过AWS System Manager Session Manager连接服务器" 