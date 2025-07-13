#!/bin/bash

# InterviewPro 部署前检查脚本
# 使用方法: ./deploy_checklist.sh

echo "🔍 InterviewPro 部署前检查开始..."
echo "=================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. 检查Docker环境
echo "1. 检查Docker环境..."
if command -v docker &> /dev/null; then
    check_pass "Docker已安装"
    docker --version
else
    check_fail "Docker未安装"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    check_pass "Docker Compose已安装"
    docker-compose --version
else
    check_fail "Docker Compose未安装"
    exit 1
fi

# 2. 检查必要文件
echo -e "\n2. 检查必要文件..."
required_files=(
    "docker-compose.prod.yml"
    "backend/Dockerfile.prod"
    "backend/requirements.txt"
    "backend/run_complete.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        check_pass "文件存在: $file"
    else
        check_fail "文件缺失: $file"
    fi
done

# 3. 检查requirements.txt完整性
echo -e "\n3. 检查Python依赖..."
if [ -f "backend/requirements.txt" ]; then
    critical_deps=(
        "Flask"
        "gunicorn"
        "numpy"
        "opencv-python-headless"
        "pytesseract"
        "PyMySQL"
        "redis"
    )
    
    for dep in "${critical_deps[@]}"; do
        if grep -q "$dep" backend/requirements.txt; then
            check_pass "依赖包: $dep"
        else
            check_fail "缺少依赖: $dep"
        fi
    done
fi

# 4. 检查系统资源
echo -e "\n4. 检查系统资源..."
available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
total_memory=$(free -m | awk 'NR==2{printf "%.0f", $2}')

echo "总内存: ${total_memory}MB"
echo "可用内存: ${available_memory}MB"

if [ "$available_memory" -gt 500 ]; then
    check_pass "内存充足 (${available_memory}MB)"
else
    check_warn "内存不足 (${available_memory}MB)，建议添加Swap"
fi

# 检查磁盘空间
available_disk=$(df -h . | awk 'NR==2 {print $4}')
echo "可用磁盘空间: $available_disk"

# 5. 检查端口占用
echo -e "\n5. 检查端口占用..."
ports=(80 3306 6379 8080)
for port in "${ports[@]}"; do
    if netstat -tuln | grep -q ":$port "; then
        check_warn "端口 $port 已被占用"
    else
        check_pass "端口 $port 可用"
    fi
done

# 6. 检查Swap配置
echo -e "\n6. 检查Swap配置..."
swap_total=$(free -m | awk '/^Swap:/ {print $2}')
if [ "$swap_total" -gt 0 ]; then
    check_pass "Swap已配置 (${swap_total}MB)"
else
    check_warn "未配置Swap，在内存不足时可能出现问题"
fi

# 7. Docker配置验证
echo -e "\n7. 验证Docker配置..."
if [ -f "docker-compose.prod.yml" ]; then
    if docker-compose -f docker-compose.prod.yml config &> /dev/null; then
        check_pass "Docker Compose配置有效"
    else
        check_fail "Docker Compose配置有错误"
        docker-compose -f docker-compose.prod.yml config
    fi
fi

echo -e "\n=================================="
echo "🔍 部署前检查完成"
echo "=================================="

# 生成建议
echo -e "\n📋 部署建议:"
echo "1. 如果内存不足，建议先创建Swap分区"
echo "2. 确保所有必要端口未被占用"
echo "3. 建议先进行本地测试"
echo "4. 分阶段部署：MySQL->Redis->Backend->Nginx"
echo -e "\n使用以下命令开始部署:"
echo "  ./deploy_staged.sh" 