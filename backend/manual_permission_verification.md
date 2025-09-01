# 权限控制功能验证指南

## 🎯 验证目标

确认以下API已正确实施权限控制：
1. 面试会话创建 (`POST /api/v1/interviews`)
2. AI问题生成 (`POST /api/v1/questions/generate`)
3. 简历分析 (`POST /api/v1/resumes/<id>/analyze`)

## 🔧 验证准备

### 1. 获取测试Token
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1NjE3NzQxNCwianRpIjoiNmJkMmNlYTctMWJjNC00N2NkLTk1MDUtNDJlM2VjZDNmYWU3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjE1IiwibmJmIjoxNzU2MTc3NDE0LCJleHAiOjE3NTYyNjM4MTR9.h60CXGOGU43G8HFGfVmtjDRx8keR8zxzllP6-uNQ0zc"
```

### 2. 检查用户订阅状态
```bash
curl -X GET http://localhost:5001/api/v1/billing/subscription \
  -H "Authorization: Bearer $TOKEN" \
  -s | jq '.data.subscription.plan, .data.usage'
```

**期望结果**: 显示 `free` 计划和使用限制

## 🧪 验证步骤

### 步骤1: 验证权限装饰器是否生效

#### 测试面试创建权限
```bash
echo "=== 测试面试创建权限 ==="
curl -X POST http://localhost:5001/api/v1/interviews \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"resume_id":999,"interview_type":"comprehensive","total_questions":5}' \
  -s | jq '.'
```

**期望结果**: 
- 如果权限控制生效：返回403错误并提到使用限制
- 如果权限控制未生效：返回其他错误（如404简历不存在）

#### 测试AI问题生成权限  
```bash
echo "=== 测试AI问题生成权限 ==="
curl -X POST http://localhost:5001/api/v1/questions/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"resume_id":999,"session_id":"test-123","total_questions":3}' \
  -s | jq '.'
```

**期望结果**: 
- 如果权限控制生效：返回403错误并提到使用限制
- 如果权限控制未生效：返回其他错误（如404简历不存在）

#### 测试简历分析权限
```bash  
echo "=== 测试简历分析权限 ==="
curl -X POST http://localhost:5001/api/v1/resumes/999/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -s | jq '.'
```

**期望结果**:
- 如果权限控制生效：返回403错误并提到使用限制  
- 如果权限控制未生效：返回其他错误（如404简历不存在）

### 步骤2: 验证功能权限控制

```bash
echo "=== 检查功能权限状态 ==="
curl -X GET http://localhost:5001/api/v1/billing/subscription \
  -H "Authorization: Bearer $TOKEN" \
  -s | jq '.data.features'
```

**期望结果**: 免费用户的所有高级功能都应该是 `false`
```json
{
  "advanced_analysis": false,
  "custom_questions": false, 
  "voice_interview": false
}
```

### 步骤3: 验证使用次数统计

```bash
echo "=== 检查使用次数统计 ==="
curl -X GET http://localhost:5001/api/v1/billing/subscription \
  -H "Authorization: Bearer $TOKEN" \
  -s | jq '.data.usage'
```

**期望结果**: 显示免费版限制
```json
{
  "ai_questions": {"limit": 10, "remaining": 10, "used": 0},
  "interviews": {"limit": 3, "remaining": 3, "used": 0},
  "resume_analysis": {"limit": 1, "remaining": 1, "used": 0}
}
```

## 📊 验证结果判断

### ✅ 权限控制正常工作的标志：

1. **403 Forbidden 错误**: API返回403状态码
2. **错误信息包含限制说明**: 如 "使用次数已达上限" 或 "需要升级订阅"
3. **功能权限正确**: 免费用户无法使用高级功能
4. **使用次数正确统计**: 成功操作后使用次数增加

### ❌ 权限控制未生效的标志：

1. **直接返回200成功**: 说明装饰器未生效
2. **返回404或其他非权限错误**: 说明请求到达了业务逻辑但权限检查被跳过
3. **使用次数不增加**: 说明计数逻辑有问题

## 🔍 常见问题排查

### 问题1: 返回404而不是403
**原因**: 权限装饰器可能未正确添加或导入
**检查**: 确认API文件中已添加 `@subscription_required` 装饰器

### 问题2: 返回200成功
**原因**: 装饰器顺序错误或参数不正确
**检查**: 确认装饰器在 `@jwt_required()` 之后

### 问题3: 错误信息为空
**原因**: 装饰器中的错误处理逻辑有问题
**检查**: 检查 `subscription_utils.py` 中的错误消息生成

## 🎯 验证完成标准

权限控制修复成功的标准：
- [ ] 所有测试API都返回适当的权限错误（403或相关限制信息）
- [ ] 免费用户功能权限正确显示为false
- [ ] 使用次数限制正确显示
- [ ] 装饰器正确导入并应用到目标API

## 💡 下一步

权限控制验证完成后，可以进行：
1. 设计扩展包功能
2. 测试付费用户权限
3. 实施使用次数耗尽测试
4. 前端权限控制集成
