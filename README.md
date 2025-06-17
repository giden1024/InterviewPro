# InterviewGenius AI 🎯

> AI驱动的智能面试助手系统，让面试准备更高效、更智能

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Development](https://img.shields.io/badge/Status-Development-orange.svg)](#)

## 📋 项目简介

InterviewGenius AI 是一个基于人工智能的面试助手系统，旨在帮助求职者通过智能化的面试练习提升面试表现。系统通过解析简历内容，生成个性化的面试问题，并提供实时的AI反馈和评估。

### ✨ 核心特性

- 🤖 **AI智能问题生成** - 基于简历内容自动生成相关面试问题
- 🎙️ **实时语音交互** - 支持语音回答和实时转录
- 📊 **智能评估反馈** - AI驱动的回答质量评估和改进建议
- 📄 **简历智能解析** - 自动解析PDF/Word简历，提取关键信息
- 💬 **实时互动体验** - WebSocket实现的流畅实时交互
- 📈 **学习进度跟踪** - 详细的面试表现分析和历史记录

## 🚀 项目状态

**当前版本**: v0.1.0-alpha  
**开发进度**: 约30%完成  
**最新更新**: 2025年6月3日

### ✅ 已完成功能
- [x] 用户注册登录系统
- [x] JWT身份认证
- [x] WebSocket实时通信
- [x] 基础API架构
- [x] 数据库设计
- [x] Docker容器化

### 🔄 开发中功能
- [ ] 简历上传和解析
- [ ] AI问题生成引擎
- [ ] 语音转文本集成
- [ ] 前端用户界面

### 📋 计划功能
- [ ] 面试会话管理
- [ ] 智能评分系统
- [ ] 数据分析报告
- [ ] 移动端适配

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Flask 3.0
- **数据库**: SQLite (开发) / MySQL (生产)
- **缓存**: Redis
- **认证**: JWT
- **实时通信**: SocketIO + gevent-websocket
- **AI服务**: DeepSeek API

### 前端技术栈 (计划)
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件**: Shadcn/ui + TailwindCSS
- **状态管理**: Zustand
- **路由**: React Router v6

### 部署架构
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **监控**: Prometheus + Grafana (计划)

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+ (前端)
- MySQL 8.0+ (生产环境)
- Redis 6.0+ (可选)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/interview-genius-ai.git
cd interview-genius-ai
```

2. **后端设置**
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

3. **前端设置** (待实现)
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

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

### 用户认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/profile` - 获取用户信息

### 简历管理 (开发中)
- `GET /api/v1/resumes` - 简历列表
- `POST /api/v1/resumes` - 上传简历

### 面试功能 (开发中)
- `GET /api/v1/interviews` - 面试列表
- `POST /api/v1/interviews/start` - 开始面试

### WebSocket事件
- `connect/disconnect` - 连接管理
- `join_interview` - 加入面试房间
- `voice_data` - 语音数据处理

## 🧪 测试

### 运行测试
```bash
# 后端测试
cd backend
python -m pytest

# WebSocket测试
python ../test_websocket.py

# API测试
curl http://localhost:5000/health
```

### 测试用户注册
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
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
│   └── requirements.txt   # Python依赖
├── frontend/              # React前端应用
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── package.json       # Node.js依赖
├── docs/                  # 项目文档
├── docker-compose.yml     # Docker编排
├── nginx.conf            # Nginx配置
└── README.md             # 项目说明
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开发文档

- [技术架构设计](docs/技术架构设计.md)
- [后端实现指南](docs/后端实现指南.md)
- [前端设计文档](docs/前端设计.md)
- [开发进度报告](docs/开发进度.md)
- [运维部署指南](docs/运维部署.md)

## 🎯 发展路线

### 近期目标 (1-2个月)
- [ ] 完成简历解析功能
- [ ] 集成AI问题生成
- [ ] 实现基础前端界面
- [ ] 语音转文本功能

### 中期目标 (3-6个月)
- [ ] 完整面试流程
- [ ] 智能评估系统
- [ ] 数据分析报告
- [ ] 移动端支持

### 长期目标 (6-12个月)
- [ ] 企业级功能
- [ ] 多语言支持
- [ ] 高级AI能力
- [ ] 社区功能

## 📞 联系我们

- **项目主页**: [GitHub Repository](https://github.com/your-username/interview-genius-ai)
- **问题反馈**: [Issues](https://github.com/your-username/interview-genius-ai/issues)
- **功能建议**: [Discussions](https://github.com/your-username/interview-genius-ai/discussions)

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢以下开源项目的支持：
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [React](https://reactjs.org/) - 前端框架
- [DeepSeek](https://www.deepseek.com/) - AI服务
- [Whisper](https://openai.com/research/whisper) - 语音识别

---

⭐ 如果这个项目对你有帮助，请给它一个星标！

**开发团队** | **最后更新**: 2025年6月3日 