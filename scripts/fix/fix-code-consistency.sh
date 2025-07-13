#!/bin/bash

# 代码一致性修复脚本
# 解决本地和服务器代码不一致问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

echo "🔧 InterviewPro 代码一致性修复工具"
echo "=================================="

# 步骤1：检查本地Git状态
log "检查本地Git状态..."
if [ ! -d ".git" ]; then
    error "当前目录不是Git仓库！"
    exit 1
fi

# 显示修改的文件
MODIFIED_FILES=$(git status --porcelain | wc -l)
log "发现 ${MODIFIED_FILES} 个文件有变更"

if [ $MODIFIED_FILES -gt 0 ]; then
    warn "以下文件有未提交的修改："
    git status --short
    
    echo ""
    read -p "是否要提交所有本地修改？(y/N): " commit_local
    
    if [[ $commit_local =~ ^[Yy]$ ]]; then
        log "提交本地修改..."
        
        # 添加所有修改的文件
        git add .
        
        # 提交修改
        COMMIT_MSG="sync: 修复代码一致性问题 - 提交所有本地修改"
        git commit -m "$COMMIT_MSG"
        
        # 推送到远程
        log "推送到远程仓库..."
        git push origin main
        
        success "本地修改已提交并推送到远程仓库"
    else
        warn "跳过本地修改提交"
    fi
fi

# 步骤2：检查服务器连接
log "检查服务器连接..."
SERVER_USER="ubuntu"
SERVER_IP="3.14.247.189"
SSH_KEY="$HOME/.ssh/aws-myy-rsa.pem"

if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$SERVER_USER@$SERVER_IP" "echo 'connected'" > /dev/null 2>&1; then
    error "无法连接到服务器 $SERVER_IP"
    exit 1
fi

success "服务器连接正常"

# 步骤3：检查服务器上的项目状态
log "检查服务器项目状态..."
SERVER_PROJECT_DIR="/home/ubuntu/InterviewPro"

# 检查是否是Git仓库
IS_GIT_REPO=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "cd $SERVER_PROJECT_DIR && [ -d .git ] && echo 'yes' || echo 'no'")

if [ "$IS_GIT_REPO" = "no" ]; then
    warn "服务器上的项目不是Git仓库"
    
    echo ""
    read -p "是否要在服务器上初始化Git仓库？(y/N): " init_git
    
    if [[ $init_git =~ ^[Yy]$ ]]; then
        log "在服务器上初始化Git仓库..."
        
        # 获取远程仓库URL
        REMOTE_URL=$(git remote get-url origin)
        
        ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "
            cd $SERVER_PROJECT_DIR
            
            # 备份当前项目
            if [ ! -d ../InterviewPro-backup-\$(date +%Y%m%d-%H%M%S) ]; then
                cp -r . ../InterviewPro-backup-\$(date +%Y%m%d-%H%M%S)/
            fi
            
            # 初始化Git仓库
            git init
            git remote add origin $REMOTE_URL
            
            # 拉取最新代码
            git fetch origin main
            git reset --hard origin/main
        "
        
        success "服务器Git仓库初始化完成"
    else
        warn "跳过Git仓库初始化"
    fi
else
    log "服务器上已是Git仓库，检查同步状态..."
    
    # 检查服务器的提交历史
    SERVER_COMMIT=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "cd $SERVER_PROJECT_DIR && git rev-parse HEAD 2>/dev/null || echo 'unknown'")
    LOCAL_COMMIT=$(git rev-parse HEAD)
    
    if [ "$SERVER_COMMIT" != "$LOCAL_COMMIT" ]; then
        warn "服务器和本地提交不一致"
        warn "本地提交: $LOCAL_COMMIT"
        warn "服务器提交: $SERVER_COMMIT"
        
        echo ""
        read -p "是否要同步服务器代码到最新版本？(y/N): " sync_server
        
        if [[ $sync_server =~ ^[Yy]$ ]]; then
            log "同步服务器代码..."
            
            ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "
                cd $SERVER_PROJECT_DIR
                git fetch origin main
                git reset --hard origin/main
            "
            
            success "服务器代码已同步到最新版本"
        fi
    else
        success "服务器和本地代码已同步"
    fi
fi

# 步骤4：重新部署服务
echo ""
read -p "是否要重新部署服务以确保代码一致性？(y/N): " redeploy

if [[ $redeploy =~ ^[Yy]$ ]]; then
    log "重新部署服务..."
    
    if [ -f "deploy-unified.sh" ]; then
        ./deploy-unified.sh
    else
        warn "未找到统一部署脚本，使用备用方案..."
        
        # 简单的重启服务
        ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "
            cd $SERVER_PROJECT_DIR
            docker-compose down
            docker-compose up -d --build
        "
    fi
    
    success "服务重新部署完成"
fi

# 步骤5：验证部署
log "验证部署状态..."
HEALTH_CHECK=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "curl -s -o /dev/null -w '%{http_code}' http://localhost:80/ || echo 'failed'")

if [ "$HEALTH_CHECK" = "200" ]; then
    success "网站访问正常 (HTTP 200)"
else
    warn "网站访问异常 (HTTP $HEALTH_CHECK)"
fi

echo ""
echo "🎉 代码一致性修复完成！"
echo ""
echo "📋 修复摘要："
echo "- 本地修改: ${MODIFIED_FILES} 个文件"
echo "- 服务器状态: $([[ $IS_GIT_REPO == "yes" ]] && echo "Git仓库" || echo "非Git仓库")"
echo "- 健康检查: $([[ $HEALTH_CHECK == "200" ]] && echo "✅ 正常" || echo "⚠️ 异常")"
echo ""
echo "💡 建议："
echo "1. 定期使用 git status 检查本地修改"
echo "2. 使用 deploy-unified.sh 进行部署"
echo "3. 设置定时任务检查代码一致性" 