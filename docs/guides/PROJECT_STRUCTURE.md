# InterviewPro 项目结构

## 项目概述
InterviewPro 是一个AI驱动的面试平台，提供智能面试练习、实时辅助和专业简历优化服务。

## 目录结构

```
InterviewPro/
├── backend/                    # 后端服务
│   ├── app/                   # Flask应用主目录
│   │   ├── __init__.py       # Flask应用初始化
│   │   ├── models/           # 数据模型
│   │   ├── routes/           # API路由
│   │   ├── services/         # 业务逻辑服务
│   │   └── utils/            # 工具函数
│   ├── tests/                 # 测试文件（已整理分类）
│   │   ├── auth/             # 认证相关测试 (5个文件)
│   │   │   ├── test_auth_功能验证.py
│   │   │   ├── test_minimal_auth.py
│   │   │   ├── minimal_auth_test.py
│   │   │   ├── debug_auth.py
│   │   │   └── 简单认证测试.py
│   │   ├── ai/               # AI功能测试 (5个文件)
│   │   │   ├── test_ai_question_generation.py
│   │   │   ├── test_ai_question_system.py
│   │   │   ├── demo_ai_question_generation.py
│   │   │   ├── simple_ai_test.py
│   │   │   └── test_deepseek_integration.py
│   │   ├── pdf/              # PDF处理测试 (2个文件)
│   │   │   ├── test_pdf_upload.py
│   │   │   └── test_pdf_parse.py
│   │   ├── websocket/        # WebSocket通信测试 (2个文件)
│   │   │   ├── test_websocket.py
│   │   │   └── test_websocket_advanced.py
│   │   ├── analysis/         # 面试分析测试 (2个文件)
│   │   │   ├── test_interview_analysis.py
│   │   │   └── simple_analysis_test.py
│   │   ├── utils/            # 工具类和通用测试 (4个文件)
│   │   │   ├── check_project.py
│   │   │   ├── create_test_data.py
│   │   │   ├── test_password_hash.py
│   │   │   └── test_resume_management.py
│   │   └── README.md         # 测试目录说明
│   ├── testfiles/            # 测试用文件
│   ├── uploads/              # 上传文件存储
│   ├── logs/                 # 日志文件
│   ├── instance/             # Flask实例配置
│   ├── migrations/           # 数据库迁移文件
│   ├── venv/                 # Python虚拟环境
│   ├── requirements.txt      # Python依赖
│   ├── run.py               # 应用启动文件
│   ├── init_db.py           # 数据库初始化
│   ├── voice_transcription_demo.py  # 语音转录演示
│   └── run_websocket.py     # WebSocket服务启动
├── frontend/                  # 前端应用
│   ├── src/                  # 源代码
│   │   ├── components/       # React组件
│   │   │   └── OfferotterHome/  # 主页组件
│   │   │       ├── OfferotterHome.tsx
│   │   │       ├── types.ts
│   │   │       ├── index.ts
│   │   │       ├── images/   # 组件图标
│   │   │       ├── __tests__/
│   │   │       └── README.md
│   │   ├── pages/            # 页面组件
│   │   │   └── Home.tsx
│   │   ├── App.tsx           # 主应用组件
│   │   ├── main.tsx          # 应用入口
│   │   ├── index.css         # 全局样式
│   │   └── vite-env.d.ts     # TypeScript声明
│   ├── index.html            # HTML模板
│   ├── package.json          # 前端依赖
│   ├── tsconfig.json         # TypeScript配置
│   ├── tsconfig.node.json    # Node TypeScript配置
│   ├── vite.config.ts        # Vite构建配置
│   ├── tailwind.config.js    # Tailwind CSS配置
│   └── postcss.config.js     # PostCSS配置
├── .mastergo/                # MasterGo设计文件
│   ├── component-workflow.md
│   ├── Offerotter-home.json
│   ├── OfferotterHome-arch.md
│   └── images/               # 设计资源
├── docs/                     # 项目文档
│   └── 开发进度.md
├── docker-compose.yml        # Docker编排配置
├── init-db.sql              # 数据库初始化脚本
├── nginx.conf               # Nginx配置
├── test_pdf_upload_curl.sh  # PDF上传测试脚本
├── README.md                # 项目说明
├── PROJECT_STRUCTURE.md     # 项目结构说明（本文件）
├── OFFEROTTER_INTEGRATION_GUIDE.md  # 集成指南
└── 各种功能说明文档.md      # 功能文档
```

## 测试文件组织说明

### 测试文件分类原则
所有Python测试文件已按功能模块分类归档到 `backend/tests/` 目录下：

1. **auth/** - 用户认证和授权相关测试
2. **ai/** - AI功能（问题生成、DeepSeek集成等）测试
3. **pdf/** - PDF文件处理和解析测试
4. **websocket/** - WebSocket实时通信测试
5. **analysis/** - 面试分析和评估测试
6. **utils/** - 工具类、项目检查和通用功能测试

### 测试文件统计
- **总计**: 20个Python测试文件
- **认证测试**: 5个文件
- **AI功能测试**: 5个文件
- **PDF处理测试**: 2个文件
- **WebSocket测试**: 2个文件
- **分析功能测试**: 2个文件
- **工具类测试**: 4个文件

## 项目进度状态

### 后端开发进度 (95%)
- ✅ 用户认证系统
- ✅ 语音转录功能
- ✅ WebSocket实时通信
- ✅ AI问题生成系统
- ✅ PDF简历解析
- ✅ 面试分析功能
- ✅ 数据库设计和迁移

### 前端开发进度 (60%)
- ✅ React + TypeScript 项目架构
- ✅ Tailwind CSS 样式系统
- ✅ OfferotterHome 主页组件
- ✅ 路由系统配置
- ✅ 组件测试框架
- 🔄 其他页面组件开发中
- 🔄 后端API集成

### 整体项目完成度: 78%

## 技术栈

### 后端
- **框架**: Flask + SQLAlchemy
- **数据库**: PostgreSQL
- **AI服务**: DeepSeek API
- **实时通信**: WebSocket
- **文件处理**: PyPDF2
- **认证**: Flask-Login + bcrypt

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **路由**: React Router
- **测试**: Jest + Testing Library

### 部署
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **数据库**: PostgreSQL

## 运行说明

### 后端启动
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python run.py
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 完整环境启动
```bash
docker-compose up -d
```

## 测试运行

### 运行所有测试
```bash
cd backend
python -m pytest tests/ -v
```

### 按模块运行测试
```bash
# 认证测试
python -m pytest tests/auth/ -v

# AI功能测试
python -m pytest tests/ai/ -v

# PDF处理测试
python -m pytest tests/pdf/ -v
```

## 开发规范

1. **代码组织**: 按功能模块分类，保持清晰的目录结构
2. **测试覆盖**: 每个功能模块都有对应的测试文件
3. **文档维护**: 重要功能都有详细的说明文档
4. **版本控制**: 使用Git进行版本管理，遵循语义化版本号

## 下一步开发计划

1. 完善前端其他页面组件
2. 集成前后端API通信
3. 添加更多AI功能
4. 优化用户体验
5. 部署到生产环境 