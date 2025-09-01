#!/bin/bash

# InterviewPro 付费模块快速启动脚本

echo "🎯 InterviewPro 付费模块快速启动"
echo "=================================="

# 检查当前目录
if [ ! -f "backend/run_complete.py" ]; then
    echo "❌ 请在项目根目录执行此脚本"
    exit 1
fi

# 启动后端服务
echo "🚀 启动后端服务..."
cd backend
source venv/bin/activate

# 检查数据库表是否存在
echo "📋 检查数据库..."
python -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    if 'subscriptions' not in tables or 'payment_history' not in tables:
        print('❌ 付费相关表不存在，请先运行: python create_billing_tables.py')
        exit(1)
    else:
        print('✅ 数据库表检查通过')
"

if [ $? -ne 0 ]; then
    echo "运行数据库初始化..."
    python create_billing_tables.py
fi

echo "🌐 启动后端API服务 (端口 5001)..."
python run_complete.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 测试API
echo "🧪 测试付费API..."
curl -s http://localhost:5001/api/v1/billing/plans | grep -q "success" && echo "✅ 付费API正常" || echo "⚠️  付费API可能未启动"

echo ""
echo "🎉 后端服务已启动！"
echo ""
echo "📋 接下来的步骤:"
echo "1. 在新终端窗口启动前端服务:"
echo "   cd frontend && npm run dev"
echo ""
echo "2. 访问以下链接测试付费功能:"
echo "   - 付费计划API: http://localhost:5001/api/v1/billing/plans"
echo "   - 前端付费页面: http://localhost:3000/billing (需要先启动前端)"
echo ""
echo "3. 测试支付流程:"
echo "   - 注册/登录用户"
echo "   - 访问付费页面"
echo "   - 选择付费计划进行测试支付"
echo ""
echo "4. Creem.io 测试信息:"
echo "   - API Key: creem_test_3sd9xtWYIYo1226oBRWBoZ"
echo "   - Product ID: prod_1UsU2rK5AiyVINJuHWnPyy"
echo "   - 测试模式: 已启用"
echo ""
echo "按 Ctrl+C 停止后端服务"

# 等待用户中断
wait $BACKEND_PID
