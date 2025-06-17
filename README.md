# InterviewPro AI 🎯

> AI驱动的智能面试助手系统，让面试准备更高效、更智能

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Development](https://img.shields.io/badge/Status-75%25_Complete-brightgreen.svg)](#)

## 📋 项目简介

InterviewPro AI 是一个基于人工智能的面试助手系统，旨在帮助求职者通过智能化的面试练习提升面试表现。系统通过解析简历内容，生成个性化的面试问题，并提供实时的AI反馈和评估。

### ✨ 核心特性

- 🤖 **AI智能问题生成** - 基于简历内容自动生成相关面试问题
- 🎙️ **实时语音交互** - 支持语音回答和实时转录
- 📊 **智能评估反馈** - AI驱动的回答质量评估和改进建议
- 📄 **简历智能解析** - 自动解析PDF/Word简历，提取关键信息
- 💬 **实时互动体验** - WebSocket实现的流畅实时交互
- 📈 **学习进度跟踪** - 详细的面试表现分析和历史记录
- 🎨 **现代化UI界面** - 基于TailwindCSS的响应式设计

## 🚀 项目状态

**当前版本**: v0.2.0-beta  
**开发进度**: 约75%完成  
**最新更新**: 2025年1月3日

### ✅ 已完成功能

#### 🎨 前端系统 (95% 完成)
- ✅ **完整UI界面** - 所有主要页面UI已完成
  - 登录/注册页面 (完整 + API集成)
  - 主页/仪表板 (完整UI)
  - 用户资料页面 (完整)
  - 简历管理页面 (完整UI)
  - 职位管理页面 (完整UI)
  - 模拟面试页面 (完整UI)
  - 面试记录页面 (完整UI)
- ✅ **响应式设计** - 移动端和桌面端适配
- ✅ **现代化技术栈** - React 18 + TypeScript + TailwindCSS
- ✅ **状态管理** - Zustand轻量级状态管理
- ✅ **路由系统** - React Router v6完整配置

#### 🔐 用户认证系统 (100% 完成)
- ✅ **JWT身份认证** - 完整的token管理
- ✅ **用户注册/登录** - 前后端完整集成
- ✅ **用户信息管理** - 个人资料获取和更新
- ✅ **会话持久化** - localStorage自动保存
- ✅ **安全密码存储** - bcrypt加密

#### 🛠️ 后端API系统 (90% 完成)
- ✅ **认证API** - 完整的用户认证接口
- ✅ **简历管理API** - 上传、解析、管理功能
- ✅ **面试管理API** - 创建、进行、记录面试
- ✅ **问题生成API** - AI驱动的智能问题生成
- ✅ **分析报告API** - 面试表现分析和报告
- ✅ **WebSocket支持** - 实时通信功能
- ✅ **数据库设计** - 完整的数据模型

#### 🤖 AI功能 (85% 完成)
- ✅ **智能问题生成** - 基于简历和职位的问题生成
- ✅ **语音转文本** - Whisper集成
- ✅ **回答分析** - AI评估和反馈
- ✅ **个性化推荐** - 基于用户表现的建议

### 🔄 开发中功能

#### 📋 职位管理系统 (需要完善)
- ⚠️ **职位CRUD操作** - 后端API需要实现
- ⚠️ **职位链接解析** - 自动解析招聘网站
- ⚠️ **职位简历匹配** - AI匹配度分析

#### 🔧 前端服务集成 (70% 完成)
- ✅ **认证服务** - authService.ts完成
- ❌ **职位服务** - jobService.ts需要创建
- ❌ **简历服务** - resumeService.ts需要创建
- ❌ **面试服务** - interviewService.ts需要创建

### 📋 计划功能
- [ ] 企业级多用户支持
- [ ] 高级数据分析和可视化
- [ ] 移动端原生应用
- [ ] 多语言支持
- [ ] 社区功能和分享

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Flask 3.0 + SQLAlchemy
- **数据库**: SQLite (开发) / MySQL (生产)
- **缓存**: Redis
- **认证**: JWT (Flask-JWT-Extended)
- **实时通信**: SocketIO + gevent-websocket
- **AI服务**: OpenAI API + Whisper
- **文件处理**: PyPDF2, python-docx
- **语音处理**: SpeechRecognition, pydub

### 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件**: TailwindCSS + 自定义组件
- **状态管理**: Zustand
- **路由**: React Router v6
- **HTTP客户端**: Axios
- **类型安全**: TypeScript 5.0

### 部署架构
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **进程管理**: Gunicorn + gevent
- **监控**: 日志系统 + 健康检查

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- Git

### 安装步骤

1. **克隆项目**
```bash
git clone <your-repo-url>
cd InterviewPro
```

2. **后端设置**
```bash
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r backend/requirements.txt

# 初始化数据库
cd backend
python init_db.py

# 启动后端服务
python run_simple.py
```

3. **前端设置**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

4. **访问应用**
- 前端: http://localhost:3000
- 后端API: http://localhost:5001
- 健康检查: http://localhost:5001/health

### 使用Docker启动

```bash
# 启动完整服务栈
docker-compose up -d

# 查看服务状态
docker-compose ps
```

## 📖 API文档

### 基础端点
- `GET /` - 服务状态
- `GET /health` - 健康检查

### 用户认证 (`/api/v1/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /profile` - 获取用户信息
- `POST /logout` - 用户登出

### 简历管理 (`/api/v1/resumes`)
- `GET /` - 简历列表
- `POST /` - 上传简历
- `GET /{id}` - 简历详情
- `DELETE /{id}` - 删除简历
- `POST /{id}/analyze` - 分析简历

### 面试功能 (`/api/v1/interviews`)
- `POST /` - 创建面试会话
- `GET /` - 面试列表
- `POST /{session_id}/start` - 开始面试
- `GET /{session_id}/next` - 获取下一个问题
- `POST /{session_id}/answer` - 提交答案
- `POST /{session_id}/end` - 结束面试

### 问题管理 (`/api/v1/questions`)
- `GET /` - 问题列表
- `POST /generate` - 生成问题
- `GET /session/{session_id}` - 获取会话问题

### 分析报告 (`/api/v1/analysis`)
- `GET /session/{session_id}` - 分析面试会话
- `GET /report/{session_id}` - 生成面试报告
- `GET /statistics` - 用户统计

### WebSocket事件
- `connect/disconnect` - 连接管理
- `join_interview` - 加入面试房间
- `voice_data` - 语音数据处理

## 🧪 测试

### API测试
```bash
# 健康检查
curl http://localhost:5001/health

# 用户注册
curl -X POST http://localhost:5001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","username":"testuser"}'

# 用户登录
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 完整API测试
```bash
# 运行完整API测试套件
cd backend
python test_all_apis.py
```

## 📁 项目结构

```
InterviewPro/
├── backend/                 # Flask后端服务
│   ├── app/                # 应用核心代码
│   │   ├── models/         # 数据模型
│   │   ├── api/           # REST API
│   │   ├── services/      # 业务逻辑
│   │   ├── websocket/     # WebSocket处理
│   │   └── utils/         # 工具函数
│   ├── tests/             # 测试文件
│   ├── uploads/           # 文件上传目录
│   ├── requirements.txt   # Python依赖
│   ├── run_simple.py      # 简化启动脚本
│   └── init_db.py         # 数据库初始化
├── frontend/              # React前端应用
│   ├── src/               # 源代码
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   ├── stores/        # 状态管理
│   │   └── types/         # TypeScript类型
│   ├── public/            # 静态资源
│   └── package.json       # Node.js依赖
├── docs/                  # 项目文档
├── docker-compose.yml     # Docker编排
├── nginx.conf            # Nginx配置
└── README.md             # 项目说明
```

## 📊 完成度统计

| 模块 | 完成度 | 状态 | 说明 |
|------|--------|------|------|
| **前端UI** | 95% | ✅ 优秀 | 所有页面UI完成，响应式设计 |
| **用户认证** | 100% | ✅ 完成 | 前后端完整集成 |
| **后端API** | 90% | ✅ 优秀 | 核心API完成，职位API待完善 |
| **AI功能** | 85% | ✅ 良好 | 问题生成和分析完成 |
| **数据库** | 95% | ✅ 优秀 | 完整数据模型和迁移 |
| **WebSocket** | 90% | ✅ 良好 | 实时通信功能完成 |
| **文件处理** | 85% | ✅ 良好 | 简历上传和解析完成 |
| **测试覆盖** | 60% | ⚠️ 一般 | API测试完成，需要单元测试 |

**总体完成度: 75%**

## 🎯 下一步计划

### 🔴 高优先级 (本周)
1. **完善职位管理API** - 实现完整的职位CRUD操作
2. **创建前端服务层** - jobService.ts, resumeService.ts等
3. **修复已知问题** - SVG组件错误等

### 🟡 中优先级 (下周)
1. **增强面试功能** - 实时语音交互优化
2. **完善数据分析** - 可视化图表和报告
3. **性能优化** - 代码分割和懒加载

### 🟢 低优先级 (后期)
1. **企业级功能** - 多租户支持
2. **移动端适配** - PWA或原生应用
3. **国际化** - 多语言支持

## 🐛 已知问题

1. **前端SVG组件错误** - JobPage.tsx中SVG标签未正确闭合
2. **PyAudio安装失败** - macOS上缺少portaudio.h头文件
3. **职位管理API缺失** - 需要实现完整的职位管理后端

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开发文档

- [项目完成状态](PROJECT_COMPLETION_STATUS.md)
- [业务API分析](BUSINESS_API_ANALYSIS.md)
- [项目结构说明](PROJECT_STRUCTURE.md)
- [AI功能说明](AI面试问题生成功能说明.md)
- [用户认证说明](用户注册登录功能说明.md)

## 🎯 发展路线

### 近期目标 (1个月)
- [x] 完成核心UI界面
- [x] 实现用户认证系统
- [x] 完成AI问题生成
- [ ] 完善职位管理功能
- [ ] 优化面试体验

### 中期目标 (3个月)
- [ ] 企业级功能支持
- [ ] 高级数据分析
- [ ] 移动端应用
- [ ] 性能优化

### 长期目标 (6个月)
- [ ] 多语言支持
- [ ] 社区功能
- [ ] 开放API平台
- [ ] 商业化部署

## 📞 联系我们

- **项目主页**: [GitHub Repository](https://github.com/your-username/InterviewPro)
- **问题反馈**: [Issues](https://github.com/your-username/InterviewPro/issues)
- **功能建议**: [Discussions](https://github.com/your-username/InterviewPro/discussions)

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢以下开源项目的支持：
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [React](https://reactjs.org/) - 前端框架
- [TailwindCSS](https://tailwindcss.com/) - CSS框架
- [OpenAI](https://openai.com/) - AI服务
- [Whisper](https://openai.com/research/whisper) - 语音识别

---

⭐ 如果这个项目对你有帮助，请给它一个星标！

**开发状态**: 🚀 积极开发中 | **最后更新**: 2025年1月3日 