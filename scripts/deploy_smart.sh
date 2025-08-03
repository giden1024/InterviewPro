#!/bin/bash
# 智能部署脚本 - 根据修改内容自动选择部署方式
set -e

echo "🧠 智能部署检测..."

# 检查修改的文件
CHANGED_FILES=$(git status --porcelain | awk '{print $2}')
echo "📋 检测到修改的文件:"
echo "$CHANGED_FILES"

# 检查是否有依赖包修改
DEPS_CHANGED=false
if echo "$CHANGED_FILES" | grep -E "(requirements\.txt|package\.json|Dockerfile)" > /dev/null; then
    DEPS_CHANGED=true
fi

# 检查是否有数据库模型修改
DB_CHANGED=false
if echo "$CHANGED_FILES" | grep -E "(models/|migrations/)" > /dev/null; then
    DB_CHANGED=true
fi

# 检查是否只有前端修改
FRONTEND_ONLY=false
if echo "$CHANGED_FILES" | grep -v "frontend/" | wc -l | grep -q "^0$"; then
    FRONTEND_ONLY=true
fi

# 检查是否只有后端代码修改 (不包括依赖和模型)
BACKEND_CODE_ONLY=false
if echo "$CHANGED_FILES" | grep -E "backend/app/.*\.py$" > /dev/null && [ "$DEPS_CHANGED" = false ] && [ "$DB_CHANGED" = false ]; then
    BACKEND_CODE_ONLY=true
fi

echo "🔍 部署策略分析:"
echo "  依赖包修改: $DEPS_CHANGED"
echo "  数据库修改: $DB_CHANGED"
echo "  仅前端修改: $FRONTEND_ONLY"
echo "  仅后端代码修改: $BACKEND_CODE_ONLY"

# 提交代码到 Git
echo "💾 提交代码..."
git add .
git commit -m "Smart deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push origin main

# 选择部署策略
if [ "$DEPS_CHANGED" = true ] || [ "$DB_CHANGED" = true ]; then
    echo "🏗️  检测到依赖或数据库修改，使用完整重构建部署..."
    ./scripts/deploy_full_rebuild.sh
elif [ "$FRONTEND_ONLY" = true ]; then
    echo "🎨 检测到仅前端修改，使用前端热更新..."
    ./scripts/deploy_frontend_only.sh
elif [ "$BACKEND_CODE_ONLY" = true ]; then
    echo "🔥 检测到仅后端代码修改，使用热更新..."
    ./scripts/deploy_hot_update.sh
else
    echo "🔄 使用服务重启部署..."
    # 直接在这里执行重启逻辑，避免递归调用
    echo "🌐 服务器重启部署..."
    ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 << 'EOF'
        cd /home/ec2-user/InterviewPro
        
        # 强制拉取最新代码 (处理文件冲突)
        git reset --hard HEAD
        git clean -fd
        git pull
        
        # 检查哪些服务需要重启
        echo "🔍 检查服务状态..."
        docker-compose -f docker-compose.prod.yml ps
        
        # 重启后端服务 (保持数据库和Redis运行)
        echo "🔄 重启后端服务..."
        docker-compose -f docker-compose.prod.yml restart backend
        
        # 重新构建并重启前端 (如果有前端修改)
        if git diff HEAD~1 --name-only | grep -q "frontend/"; then
            echo "🔄 重新构建前端..."
            cd frontend
            npm run build
            cd ..
            docker-compose -f docker-compose.prod.yml restart nginx
        fi
        
        # 等待服务启动
        sleep 10
        
        echo "✅ 服务重启完成"
EOF
    
    echo "🎉 重启部署完成！"
    
    # 验证部署
    echo "🔍 验证服务状态..."
    ssh -i ~/.ssh/aws-myy-rsa.pem ec2-user@3.138.194.143 'docker-compose -f /home/ec2-user/InterviewPro/docker-compose.prod.yml ps'
fi 