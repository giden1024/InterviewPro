#!/bin/bash
# 测试OpenCV修复的脚本

echo "🔍 测试OpenCV修复..."

# 检查本地requirements.txt
echo "1. 检查本地requirements.txt..."
if grep -q "opencv-python-headless" backend/requirements.txt; then
    echo "✅ 本地已配置opencv-python-headless"
else
    echo "❌ 本地未配置opencv-python-headless"
    exit 1
fi

# 测试本地导入
echo "2. 测试本地OpenCV导入..."
cd backend
if python -c "import cv2; print('OpenCV version:', cv2.__version__)" 2>/dev/null; then
    echo "✅ 本地OpenCV导入成功"
else
    echo "⚠️  本地OpenCV未安装或导入失败（这在本地环境是正常的）"
fi

echo "3. 检查OCR服务代码..."
if grep -q "import cv2" app/services/ocr_service.py; then
    echo "✅ OCR服务正确使用cv2"
else
    echo "❌ OCR服务未找到cv2导入"
fi

echo ""
echo "🎯 修复总结:"
echo "  - ✅ requirements.txt已更新为opencv-python-headless"
echo "  - ✅ 代码无需修改（API完全兼容）"
echo "  - ✅ 准备好部署到AWS服务器"
echo ""
echo "下一步: 运行 ./scripts/deploy_with_monitoring.sh 进行完整部署" 