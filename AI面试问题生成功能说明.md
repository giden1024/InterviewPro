# AI面试问题生成功能说明

## 功能概述

InterviewGenius AI新增了基于简历信息的个性化面试问题生成功能，能够根据用户上传的简历自动生成符合其技能背景和经验的面试问题。

## 主要特性

### 🤖 智能问题生成
- **基于简历分析**: 根据解析出的技能、教育背景、工作经验等信息生成个性化问题
- **多种问题类型**: 支持技术问题、行为问题、经验问题、情景问题和通用问题
- **难度分级**: 提供简单、中等、困难三种难度级别
- **AI驱动**: 使用OpenAI GPT模型生成高质量问题

### 🎯 面试类型支持
1. **技术面试**: 主要考察技术技能和编程能力
2. **HR面试**: 主要考察行为表现和团队协作能力  
3. **综合面试**: 技术和行为能力的综合考察

### 📊 完整面试流程
- **会话管理**: 创建、开始、暂停、结束面试会话
- **进度跟踪**: 实时跟踪面试进度和完成情况
- **答案记录**: 支持文本和音频答案提交
- **统计分析**: 提供详细的面试统计信息

## API接口说明

### 创建面试会话
```http
POST /api/v1/interviews
Content-Type: application/json
Authorization: Bearer <token>

{
    "resume_id": 1,
    "interview_type": "comprehensive",
    "total_questions": 10,
    "custom_title": "我的技术面试",
    "difficulty_distribution": {
        "easy": 3,
        "medium": 5, 
        "hard": 2
    }
}
```

### 获取面试会话详情
```http
GET /api/v1/interviews/{session_id}
Authorization: Bearer <token>
```

### 开始面试
```http
POST /api/v1/interviews/{session_id}/start
Authorization: Bearer <token>
```

### 获取下一个问题
```http
GET /api/v1/interviews/{session_id}/next
Authorization: Bearer <token>
```

### 提交答案
```http
POST /api/v1/interviews/{session_id}/answer
Content-Type: application/json
Authorization: Bearer <token>

{
    "question_id": 1,
    "answer_text": "我的回答内容...",
    "response_time": 120
}
```

### 获取面试类型
```http
GET /api/v1/interviews/types
```

### 获取统计信息
```http
GET /api/v1/interviews/statistics
Authorization: Bearer <token>
```

## 数据库模型

### Question (问题模型)
```python
- id: 问题ID
- resume_id: 关联简历ID
- user_id: 用户ID
- question_text: 问题内容
- question_type: 问题类型 (technical, behavioral, experience, situational, general)
- difficulty: 难度级别 (easy, medium, hard)
- category: 具体分类 (如 "Python", "项目管理")
- tags: 标签列表
- expected_answer: 期望答案
- evaluation_criteria: 评估标准
- ai_context: AI生成上下文
```

### InterviewSession (面试会话模型)
```python
- id: 会话ID
- session_id: UUID
- user_id: 用户ID
- resume_id: 简历ID
- title: 面试标题
- interview_type: 面试类型
- total_questions: 总问题数
- status: 会话状态 (created, in_progress, completed)
- current_question_index: 当前问题索引
- difficulty_distribution: 难度分布
- type_distribution: 类型分布
```

### Answer (答案模型)
```python
- id: 答案ID
- session_id: 会话ID
- question_id: 问题ID
- user_id: 用户ID
- answer_text: 答案文本
- answer_audio_path: 音频文件路径
- score: 评分 (0-100)
- ai_feedback: AI反馈
- response_time: 回答用时
```

## 使用流程

### 1. 准备工作
1. 用户注册/登录获取访问令牌
2. 上传简历并等待解析完成
3. 配置OpenAI API密钥

### 2. 创建面试会话
```javascript
const response = await fetch('/api/v1/interviews', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        resume_id: resumeId,
        interview_type: 'comprehensive',
        total_questions: 10
    })
});

const result = await response.json();
const sessionId = result.data.session_id;
```

### 3. 开始面试
```javascript
const startResponse = await fetch(`/api/v1/interviews/${sessionId}/start`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

const startResult = await startResponse.json();
const firstQuestion = startResult.data.next_question;
```

### 4. 面试过程
```javascript
// 获取当前问题
const questionResponse = await fetch(`/api/v1/interviews/${sessionId}/next`, {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

// 提交答案
const answerResponse = await fetch(`/api/v1/interviews/${sessionId}/answer`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        question_id: questionId,
        answer_text: userAnswer,
        response_time: timeSpent
    })
});
```

## AI问题生成机制

### 生成策略
1. **上下文分析**: 提取简历中的关键信息
2. **类型分配**: 根据面试类型分配问题类型比例
3. **难度平衡**: 按照指定分布生成不同难度问题
4. **个性化**: 结合候选人技能和经验定制问题
5. **质量保证**: 包含期望答案和评估标准

### 问题质量要素
- **相关性**: 与候选人技能和经验高度相关
- **层次性**: 从基础概念到深层应用
- **实用性**: 贴近实际工作场景
- **评估性**: 便于评估候选人能力

### AI提示工程
系统使用精心设计的提示模板，确保生成的问题：
- 语言清晰准确
- 逻辑结构合理
- 评估目标明确
- 难度级别适当

## 配置说明

### 环境变量
```bash
# OpenAI配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# 默认配置
DEFAULT_QUESTIONS_COUNT=10
DEFAULT_DIFFICULTY_DISTRIBUTION={"easy": 3, "medium": 5, "hard": 2}
```

### 面试类型配置
```python
# 技术面试
TECHNICAL_DISTRIBUTION = {
    "technical": 6,
    "experience": 2,
    "situational": 2
}

# HR面试  
HR_DISTRIBUTION = {
    "behavioral": 4,
    "experience": 3,
    "situational": 2,
    "general": 1
}

# 综合面试
COMPREHENSIVE_DISTRIBUTION = {
    "technical": 3,
    "behavioral": 3,
    "experience": 2,
    "situational": 2
}
```

## 测试验证

### 运行测试脚本
```bash
python test_ai_question_generation.py
```

测试脚本将验证：
- 用户认证流程
- 简历上传和解析
- 面试会话创建
- AI问题生成质量
- 完整面试流程
- 统计信息获取

### 测试案例
1. **技术面试**: 验证技术问题的生成质量和相关性
2. **HR面试**: 验证行为问题的设计和评估标准
3. **综合面试**: 验证不同类型问题的平衡分配
4. **边界情况**: 测试异常情况的处理

## 性能优化

### 缓存策略
- 问题模板缓存
- 用户会话缓存
- AI响应缓存

### 并发处理
- 异步AI调用
- 批量问题生成
- 数据库连接池

### 成本控制
- Token使用监控
- 请求频率限制
- 备用问题库

## 扩展功能

### 未来规划
1. **答案评估**: AI自动评估用户答案质量
2. **实时反馈**: 面试过程中的即时建议
3. **面试报告**: 生成详细的面试分析报告
4. **多语言支持**: 支持多种语言的面试问题
5. **视频面试**: 集成视频通话功能

### 集成可能
- 与招聘系统集成
- 与学习平台对接
- 与职业规划工具整合

## 注意事项

### 安全考虑
- API密钥安全存储
- 用户数据隐私保护
- 访问权限控制

### 错误处理
- AI服务不可用时的备用方案
- 网络异常的重试机制
- 数据完整性检查

### 监控告警
- API调用成功率监控
- 响应时间监控
- 错误率告警

## 技术支持

如有问题或需要技术支持，请联系开发团队或查看详细的API文档。

---

**InterviewGenius AI** - 让面试更智能，让求职更成功！ 