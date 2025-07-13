#!/bin/bash

echo "🔧 Mock Interview 答案提交问题快速修复"
echo "=================================================="

# 检查后端服务
echo "1. 检查后端服务状态..."
if curl -s "http://localhost:5001/" > /dev/null; then
    echo "   ✅ 后端服务正常运行"
else
    echo "   ❌ 后端服务未运行，请先启动后端服务："
    echo "   cd backend && source venv/bin/activate && python run.py"
    exit 1
fi

# 创建测试用户
echo ""
echo "2. 创建测试用户..."
REGISTER_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"mocktest@example.com","password":"password123","username":"Mock Test User"}' \
  "http://localhost:5001/api/v1/auth/register" 2>/dev/null)

if echo "$REGISTER_RESPONSE" | grep -q '"success":true'; then
    echo "   ✅ 测试用户创建成功"
    TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
else
    echo "   ℹ️  用户可能已存在，尝试登录..."
    LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
      -d '{"email":"mocktest@example.com","password":"password123"}' \
      "http://localhost:5001/api/v1/auth/login" 2>/dev/null)
    
    if echo "$LOGIN_RESPONSE" | grep -q '"success":true'; then
        echo "   ✅ 登录成功"
        TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
    else
        echo "   ❌ 登录失败，请检查后端服务"
        echo "   响应: $LOGIN_RESPONSE"
        exit 1
    fi
fi

if [ -z "$TOKEN" ]; then
    echo "   ❌ 无法获取token"
    exit 1
fi

echo "   🔑 Token: ${TOKEN:0:50}..."

# 验证token
echo ""
echo "3. 验证token有效性..."
PROFILE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:5001/api/v1/auth/profile" 2>/dev/null)

if echo "$PROFILE_RESPONSE" | grep -q '"success":true'; then
    echo "   ✅ Token验证成功"
else
    echo "   ❌ Token验证失败"
    echo "   响应: $PROFILE_RESPONSE"
    exit 1
fi

# 生成前端设置脚本
echo ""
echo "4. 生成前端修复脚本..."

cat > fix_frontend_token.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Mock Interview Token 修复</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f8f9fa; padding: 20px; border-radius: 8px; }
        .token { background: #e9ecef; padding: 10px; font-family: monospace; word-break: break-all; }
        button { background: #007cba; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 0; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Mock Interview Token 修复工具</h1>
        
        <h3>步骤1: 设置Token</h3>
        <div class="token">$TOKEN</div>
        <button onclick="setToken()">自动设置Token</button>
        <div id="result"></div>
        
        <h3>步骤2: 验证修复</h3>
        <button onclick="testAPI()">测试API连接</button>
        <div id="apiResult"></div>
        
        <h3>步骤3: 打开Mock Interview</h3>
        <button onclick="openMockInterview()">打开Mock Interview页面</button>
    </div>

    <script>
        function setToken() {
            const token = '$TOKEN';
            localStorage.setItem('access_token', token);
            document.getElementById('result').innerHTML = '<p class="success">✅ Token已设置成功！</p>';
        }

        async function testAPI() {
            const token = localStorage.getItem('access_token');
            if (!token) {
                document.getElementById('apiResult').innerHTML = '<p class="error">❌ 请先设置Token</p>';
                return;
            }

            try {
                const response = await fetch('http://localhost:5001/api/v1/auth/profile', {
                    headers: {
                        'Authorization': \`Bearer \${token}\`
                    }
                });
                
                if (response.ok) {
                    document.getElementById('apiResult').innerHTML = '<p class="success">✅ API连接正常，可以使用Mock Interview了！</p>';
                } else {
                    document.getElementById('apiResult').innerHTML = '<p class="error">❌ API连接失败: ' + response.status + '</p>';
                }
            } catch (error) {
                document.getElementById('apiResult').innerHTML = '<p class="error">❌ 连接错误: ' + error.message + '</p>';
            }
        }

        function openMockInterview() {
            window.open('http://localhost:3000/mock-interview', '_blank');
        }

        // 页面加载时自动设置token
        window.onload = function() {
            setToken();
        };
    </script>
</body>
</html>
EOF

echo "   ✅ 修复脚本已生成: fix_frontend_token.html"

# 打开修复页面
echo ""
echo "5. 打开修复页面..."
if command -v open > /dev/null; then
    open "fix_frontend_token.html"
    echo "   ✅ 修复页面已在浏览器中打开"
else
    echo "   📋 请手动打开: $(pwd)/fix_frontend_token.html"
fi

echo ""
echo "🎉 修复完成！"
echo "=================================================="
echo "下一步操作："
echo "1. 在打开的修复页面中点击'自动设置Token'"
echo "2. 点击'测试API连接'验证"
echo "3. 点击'打开Mock Interview页面'开始使用"
echo ""
echo "如果仍有问题，请查看详细报告: MOCK_INTERVIEW_ANSWER_SUBMIT_FIX_REPORT.md" 