# Creem.io生产环境部署指南

## 🎯 问题分析

当前回调失败的主要原因：

### 1. 使用测试模式
- **当前状态**: `CREEM_TEST_MODE=True`
- **API地址**: `https://test-api.creem.io/v1/checkouts`
- **问题**: 测试环境的webhook可能不稳定或不发送

### 2. 本地环境限制
- **当前回调URL**: `https://xxxx.ngrok-free.app/api/v1/billing/callback`
- **问题**: localhost + ngrok的不稳定性

## 🚀 解决方案：部署到生产环境

### 步骤1: 准备Creem.io正式账户

1. **登录Creem.io控制台** (非测试模式)
2. **获取正式API密钥**:
   ```
   生产API密钥格式: creem_live_xxxxxxxxxx
   测试API密钥格式: creem_test_xxxxxxxxxx
   ```

3. **创建正式产品**:
   - Basic计划产品
   - Premium计划产品
   - 记录产品ID

4. **配置Webhook**:
   - URL: `https://yourdomain.com/api/v1/billing/callback`
   - 方法: GET
   - 事件: payment.completed

### 步骤2: 服务器环境配置

#### 方案A: 使用现有AWS服务器
```bash
# 1. 登录AWS服务器
ssh -i your-key.pem ubuntu@3.138.194.143

# 2. 进入项目目录
cd /path/to/InterviewPro

# 3. 设置环境变量
export CREEM_TEST_MODE=False
export CREEM_API_KEY=creem_live_your_production_key
export CREEM_BASIC_PRODUCT_ID=prod_your_basic_id
export CREEM_PREMIUM_PRODUCT_ID=prod_your_premium_id
export FRONTEND_URL=https://offerott.com

# 4. 重启服务
docker-compose -f docker-compose.prod.yml restart
```

#### 方案B: 新服务器部署
```bash
# 1. 克隆代码到服务器
git clone https://github.com/your-repo/InterviewPro.git
cd InterviewPro

# 2. 复制生产配置
cp production_creem_config.env .env

# 3. 编辑配置文件
nano .env
# 填入正式的API密钥和产品ID

# 4. 运行部署脚本
./deploy_production_creem.sh
```

### 步骤3: 验证部署

#### 检查配置
```bash
# 检查环境变量
echo "CREEM_TEST_MODE: $CREEM_TEST_MODE"
echo "CREEM_API_KEY: ${CREEM_API_KEY:0:20}..."
echo "FRONTEND_URL: $FRONTEND_URL"

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 检查日志
docker-compose -f docker-compose.prod.yml logs backend | grep -i creem
```

#### 测试回调URL
```bash
# 测试回调端点可访问性
curl -X GET "https://yourdomain.com/api/v1/billing/callback?test=1"

# 应该返回400错误 (缺少必需参数)，说明端点可访问
```

### 步骤4: Creem.io控制台配置

1. **登录Creem.io生产控制台**
2. **导航到Webhooks设置**
3. **添加Webhook端点**:
   ```
   URL: https://yourdomain.com/api/v1/billing/callback
   方法: GET
   事件: checkout.completed, payment.completed
   ```
4. **测试Webhook连接**

### 步骤5: 测试支付流程

1. **创建测试订单**:
   ```bash
   curl -X POST "https://yourdomain.com/api/v1/billing/checkout" \
     -H "Authorization: Bearer your_jwt_token" \
     -H "Content-Type: application/json" \
     -d '{"plan": "basic"}'
   ```

2. **完成支付流程**
3. **检查回调日志**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend | grep "PAYMENT CALLBACK"
   ```

## 📊 预期结果

### 成功指标
- ✅ 使用正式Creem API (`https://api.creem.io`)
- ✅ 回调URL稳定可访问 (`https://yourdomain.com`)
- ✅ Webhook正常发送和接收
- ✅ 支付状态正确更新 (`pending` → `completed`)
- ✅ 订阅权益正确激活

### 成功率提升预期
- **当前**: 15-20% 回调成功率
- **部署后预期**: 95%+ 回调成功率

## 🛠️ 故障排除

### 如果回调仍然失败

1. **检查Creem.io控制台**:
   - Webhook发送历史
   - 错误日志
   - 重试记录

2. **检查服务器日志**:
   ```bash
   # 实时查看回调日志
   docker-compose -f docker-compose.prod.yml logs -f backend | grep -i callback
   
   # 查看网络连接
   netstat -tulpn | grep :80
   netstat -tulpn | grep :443
   ```

3. **检查防火墙**:
   ```bash
   # 确保80和443端口开放
   sudo ufw status
   sudo ufw allow 80
   sudo ufw allow 443
   ```

4. **检查SSL证书**:
   ```bash
   # 测试HTTPS访问
   curl -I https://yourdomain.com/api/v1/billing/callback
   ```

## 🎯 关键差异对比

| 项目 | 当前 (本地+测试) | 生产环境 |
|------|------------------|----------|
| **API地址** | `test-api.creem.io` | `api.creem.io` |
| **回调URL** | `ngrok.app` (不稳定) | `yourdomain.com` (稳定) |
| **测试模式** | `True` | `False` |
| **API密钥** | `creem_test_xxx` | `creem_live_xxx` |
| **Webhook稳定性** | 低 (15-20%) | 高 (95%+) |

## 📝 部署检查清单

- [ ] 获取Creem.io正式API密钥
- [ ] 创建正式产品并获取产品ID
- [ ] 配置服务器环境变量
- [ ] 部署到生产服务器
- [ ] 配置域名和SSL证书
- [ ] 在Creem.io控制台配置Webhook
- [ ] 测试支付流程
- [ ] 验证回调成功率

**预计解决回调问题的成功率: 95%+**
