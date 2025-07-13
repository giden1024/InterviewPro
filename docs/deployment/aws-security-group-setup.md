# AWS安全组配置指南

## 🔒 为InterviewPro配置安全组

### 必需的入站规则

| 类型 | 协议 | 端口范围 | 来源 | 描述 |
|------|------|----------|------|------|
| SSH | TCP | 22 | 0.0.0.0/0 | SSH远程访问 |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP网站访问 |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS安全访问 |
| 自定义TCP | TCP | 5001 | 0.0.0.0/0 | 后端API服务 |
| 自定义TCP | TCP | 3000-3003 | 0.0.0.0/0 | 前端开发服务器 |

### 🛠️ 配置步骤

#### 1. AWS控制台配置

1. **登录AWS控制台**
2. **进入EC2服务**
3. **在左侧菜单选择"安全组"**
4. **找到您实例使用的安全组**
5. **点击"编辑入站规则"**
6. **添加上述规则**

#### 2. AWS CLI配置

```bash
# 获取安全组ID
aws ec2 describe-instances --instance-ids i-your-instance-id

# 添加HTTP规则
aws ec2 authorize-security-group-ingress \
    --group-id sg-your-security-group-id \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# 添加HTTPS规则
aws ec2 authorize-security-group-ingress \
    --group-id sg-your-security-group-id \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# 添加SSH规则
aws ec2 authorize-security-group-ingress \
    --group-id sg-your-security-group-id \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# 添加后端API规则
aws ec2 authorize-security-group-ingress \
    --group-id sg-your-security-group-id \
    --protocol tcp \
    --port 5001 \
    --cidr 0.0.0.0/0
```

### 🔍 验证配置

配置完成后，运行以下命令验证：

```bash
# 测试SSH连接
ssh -i your-key.pem ubuntu@3.144.27.91

# 测试HTTP访问
curl -I http://3.144.27.91

# 测试端口连通性
nc -zv 3.144.27.91 80
nc -zv 3.144.27.91 22
```

### ⚠️ 安全注意事项

1. **生产环境建议**：
   - SSH访问限制为特定IP：`your-ip/32`
   - 使用堡垒机或VPN

2. **最小权限原则**：
   - 只开放必需的端口
   - 定期审查安全组规则

3. **监控和日志**：
   - 启用VPC Flow Logs
   - 配置CloudTrail审计

### 🚨 常见问题排查

1. **仍然无法访问**：
   - 检查NACL（网络ACL）设置
   - 确认路由表配置
   - 验证实例是否在公有子网

2. **SSH连接被拒绝**：
   - 检查SSH密钥是否正确
   - 确认用户名（Ubuntu: ubuntu, Amazon Linux: ec2-user）

3. **HTTP服务无响应**：
   - 确认服务器上的应用程序正在运行
   - 检查服务器防火墙（ufw, iptables）
   - 验证应用程序绑定的IP地址（0.0.0.0 vs 127.0.0.1） 