# 📁 InterviewPro 部署文件索引

## 📋 本地部署文档

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `DEPLOYMENT_COMPLETE_REPORT.md` | 完整部署报告 | 详细记录整个部署过程和技术细节 |
| `DEPLOYMENT_STATUS_SNAPSHOT.md` | 部署状态快照 | 当前系统运行状态和快速运维指南 |
| `SSL_CERTIFICATE_SETUP_GUIDE.md` | SSL证书配置指南 | SSL证书申请和配置详细说明 |
| `DEPLOYMENT_FILES_INDEX.md` | 文件索引 | 本文档，记录所有部署相关文件 |

## 🔧 本地配置文件

| 文件名 | 描述 | 状态 |
|--------|------|------|
| `deploy-simple.sh` | 部署脚本 | ✅ 已执行 |
| `nginx.ssl.conf` | SSL Nginx配置模板 | ✅ 已上传 |
| `setup-letsencrypt.sh` | Let's Encrypt自动化脚本 | ✅ 已上传 |
| `check-dns.sh` | DNS解析检查脚本 | ✅ 已上传 |

## 🖥️ 服务器端文件

### 配置文件
```
/etc/nginx/sites-available/interviewpro-ssl    # 当前使用的SSL配置
/etc/nginx/sites-available/interviewpro-temp   # 临时配置
/etc/nginx/ssl/selfsigned.crt                  # SSL证书
/etc/nginx/ssl/selfsigned.key                  # SSL私钥
/etc/nginx/ssl/dhparam.pem                     # DH参数
```

### 应用文件
```
/opt/interviewpro/frontend/                    # 前端静态文件
├── index.html                                 # 主页面
├── assets/                                    # 静态资源
│   ├── index-*.js                            # JavaScript包
│   ├── index-*.css                           # 样式文件
│   └── images/                               # 图片资源
└── ...

/opt/interviewpro/backend/                     # 后端应用
├── venv/                                      # Python虚拟环境
├── test_backend.py                           # 生产环境后端应用
└── ...
```

### 脚本文件
```
/root/setup-letsencrypt.sh                     # Let's Encrypt证书申请脚本
/root/check-dns.sh                             # DNS状态检查脚本
```

### 日志文件
```
/var/log/nginx/access.log                      # Nginx访问日志
/var/log/nginx/error.log                       # Nginx错误日志
/var/log/letsencrypt/letsencrypt.log           # Let's Encrypt日志
~/.pm2/logs/                                   # PM2进程日志
```

## 🔄 版本控制

### Git仓库文件
- 所有部署脚本和配置文件已保存在项目根目录
- 部署文档记录在项目文档中
- 配置文件模板可复用于其他部署

### 备份建议
```bash
# 备份重要配置文件
tar -czf interviewpro-config-backup-$(date +%Y%m%d).tar.gz \
    /etc/nginx/sites-available/interviewpro-* \
    /etc/nginx/ssl/ \
    /opt/interviewpro/backend/test_backend.py \
    /root/setup-letsencrypt.sh \
    /root/check-dns.sh
```

## 📊 文档使用指南

### 快速查看部署状态
```bash
# 查看当前状态
cat DEPLOYMENT_STATUS_SNAPSHOT.md
```

### 详细了解部署过程
```bash
# 查看完整报告
cat DEPLOYMENT_COMPLETE_REPORT.md
```

### SSL证书管理
```bash
# 查看SSL配置指南
cat SSL_CERTIFICATE_SETUP_GUIDE.md
```

## 🎯 文档维护

- **更新频率**: 重大变更时更新
- **版本控制**: 使用Git跟踪变更
- **责任人**: 运维团队
- **审核**: 技术负责人

---

**创建时间**: 2025年6月26日 19:15  
**文档版本**: v1.0  
**维护状态**: 🟢 最新 