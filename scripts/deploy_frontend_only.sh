#!/bin/bash
# 前端专用部署脚本
set -e

echo "🎨 开始前端专用部署..."

# 本地构建前端
echo "🏗️  本地构建前端..."
cd frontend
npm run build
cd ..

# 提交代码
echo "💾 提交代码..."
git add .
git commit -m "Frontend update: $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push origin main

# 上传前端文件
echo "📤 上传前端文件..."
scp -i ~/.ssh/aws-myy-rsa.pem -r frontend/dist/* ec2-user@3.138.194.143:/tmp/frontend_update/

# 服务器更新前端
echo "🌐 服务器更新前端..."
ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 << 'EOF'
    # 创建临时目录
    mkdir -p /tmp/frontend_update
    
    # 备份当前前端
    docker exec interviewpro-nginx cp -r /usr/share/nginx/html /tmp/nginx_backup_$(date +%Y%m%d_%H%M%S)
    
    # 更新前端文件
    docker cp /tmp/frontend_update/. interviewpro-nginx:/usr/share/nginx/html/
    
    # 清理临时文件
    rm -rf /tmp/frontend_update
    
    echo "✅ 前端更新完成"
EOF

echo "🎉 前端部署完成！"

# 验证
echo "🔍 验证前端..."
curl -s https://offerott.com/ > /dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend check failed" 