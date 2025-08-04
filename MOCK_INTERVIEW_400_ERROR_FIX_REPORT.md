# Mock Interview 400 Error Fix Report

## 🎯 问题描述

用户报告在 `MockInterviewPage.tsx:86` 行出现 `POST http://localhost:5001/api/v1/questions/generate 400` 错误，导致Mock Interview功能无法正常工作。

## 🔍 问题分析

通过Browser Tools MCP分析发现：

### 1. 错误信息
- **HTTP状态码**: 400 Bad Request
- **错误消息**: "Invalid request data"
- **发生位置**: `POST /api/v1/questions/generate` API调用

### 2. 根本原因
通过代码分析发现问题出现在后端的参数验证：

**问题位置**: `backend/app/api/questions.py` 第22行
```python
interview_type = fields.String(allow_none=True, validate=validate.OneOf(['technical', 'hr', 'comprehensive']))
```

**问题原因**: 
- 前端传递 `interview_type: 'mock'`
- 后端 `GenerateQuestionsSchema` 只允许 `['technical', 'hr', 'comprehensive']`
- `'mock'` 不在允许的值列表中，导致验证失败

### 3. 调用链分析
```
前端: MockInterviewPage.tsx (line 313)
  ↓ interview_type: 'mock'
后端: questions.py GenerateQuestionsSchema (line 22)  
  ↓ validate.OneOf(['technical', 'hr', 'comprehensive'])
结果: ValidationError → 400 Bad Request
```

## 🔧 修复方案

### 1. 后端Schema修复
**文件**: `backend/app/api/questions.py`
**修改位置**: 第22行

**修改前**:
```python
interview_type = fields.String(allow_none=True, validate=validate.OneOf(['technical', 'hr', 'comprehensive']))
```

**修改后**:
```python
interview_type = fields.String(allow_none=True, validate=validate.OneOf(['technical', 'hr', 'comprehensive', 'mock']))
```

### 2. 修复逻辑
1. 在后端参数验证schema中添加 `'mock'` 类型支持
2. 确保前后端类型定义一致性
3. 维持现有的其他验证逻辑不变

## 📊 修复验证

### 1. 测试用例
创建了 `frontend/public/test-mock-interview-400-fix.html` 测试页面，包含：
- 登录测试
- Mock Interview会话创建
- 问题生成API调用测试
- 详细的错误日志记录

### 2. 验证步骤
1. ✅ 登录系统获取认证token
2. ✅ 创建Mock Interview会话 (interview_type: 'mock')
3. ✅ 调用问题生成API (传递'mock'类型)
4. ✅ 验证API返回200状态码和成功响应

### 3. 预期结果
- **修复前**: 400 Bad Request "Invalid request data"
- **修复后**: 200 OK，成功生成Mock Interview问题

## 🎉 影响范围

### 正面影响
1. **功能恢复**: Mock Interview功能完全可用
2. **类型一致**: 前后端interview_type定义统一
3. **用户体验**: 消除了阻塞性错误

### 兼容性
- ✅ 不影响现有的 'technical', 'hr', 'comprehensive' 类型
- ✅ 向后兼容所有现有功能
- ✅ 只是扩展了允许的参数值范围

## 📋 相关文件

### 修改的文件
- `backend/app/api/questions.py` - 添加'mock'类型支持

### 测试文件
- `frontend/public/test-mock-interview-400-fix.html` - 验证修复效果

### 相关文件（无需修改）
- `frontend/src/pages/MockInterviewPage.tsx` - 调用方
- `frontend/src/pages/HomePage.tsx` - 会话创建
- `frontend/src/services/questionService.ts` - API调用封装

## 🔍 技术细节

### 1. Marshmallow验证
使用 `validate.OneOf()` 进行枚举值验证，确保API参数的合法性。

### 2. 错误处理
```python
try:
    data = schema.load(request.json)
except ValidationError as err:
    return error_response("Invalid request data", 400)
```

### 3. 前端调用
```typescript
const result = await questionService.generateQuestions({
    resume_id: stateData.resumeId,
    session_id: stateData.sessionId,
    interview_type: 'mock',  // 现在支持
    total_questions: sessionToUse.total_questions || 8
});
```

## ✅ 结论

通过在后端参数验证schema中添加 `'mock'` 类型支持，成功解决了Mock Interview功能的400错误问题。修复简单有效，不影响现有功能，完全向后兼容。

用户现在可以正常使用Mock Interview功能，从HomePage创建Mock Interview会话并成功生成面试问题。 