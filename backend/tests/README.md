# InterviewPro 测试文件目录

本目录包含 InterviewPro 项目的所有测试文件，按功能模块进行分类组织。

## 目录结构

### `/auth` - 认证相关测试
- `test_auth_功能验证.py` - 用户认证功能完整验证
- `test_minimal_auth.py` - 最小认证功能测试
- `minimal_auth_test.py` - 简化认证测试
- `debug_auth.py` - 认证调试工具
- `简单认证测试.py` - 基础认证测试

### `/ai` - AI功能测试
- `test_ai_question_generation.py` - AI问题生成功能测试
- `test_ai_question_system.py` - AI问题系统完整测试
- `demo_ai_question_generation.py` - AI问题生成演示
- `simple_ai_test.py` - 简单AI功能测试
- `test_deepseek_integration.py` - DeepSeek集成测试

### `/pdf` - PDF处理测试
- `test_pdf_upload.py` - PDF上传功能测试
- `test_pdf_parse.py` - PDF解析功能测试

### `/websocket` - WebSocket通信测试
- `test_websocket.py` - 基础WebSocket测试
- `test_websocket_advanced.py` - 高级WebSocket功能测试

### `/analysis` - 面试分析测试
- `test_interview_analysis.py` - 面试分析功能测试
- `simple_analysis_test.py` - 简单分析测试

### `/utils` - 工具类和通用测试
- `check_project.py` - 项目状态检查工具
- `create_test_data.py` - 测试数据创建工具
- `test_password_hash.py` - 密码哈希测试
- `test_resume_management.py` - 简历管理测试

## 运行测试

### 运行所有测试
```bash
cd backend
python -m pytest tests/
```

### 运行特定模块测试
```bash
# 认证测试
python -m pytest tests/auth/

# AI功能测试
python -m pytest tests/ai/

# PDF处理测试
python -m pytest tests/pdf/

# WebSocket测试
python -m pytest tests/websocket/

# 分析功能测试
python -m pytest tests/analysis/

# 工具类测试
python -m pytest tests/utils/
```

### 运行单个测试文件
```bash
python -m pytest tests/auth/test_auth_功能验证.py
```

## 测试环境要求

1. 确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 确保数据库已初始化：
   ```bash
   python init_db.py
   ```

3. 确保环境变量已配置（如API密钥等）

## 注意事项

- 某些测试需要外部服务（如DeepSeek API），请确保相关配置正确
- PDF测试需要测试文件，位于 `backend/testfiles/` 目录
- WebSocket测试可能需要启动后端服务
- 运行测试前请检查数据库连接和相关服务状态 