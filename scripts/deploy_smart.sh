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
    ./scripts/deploy_restart.sh
fi 