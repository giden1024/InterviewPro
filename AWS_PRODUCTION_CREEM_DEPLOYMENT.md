# AWS生产环境Creem.io部署指南

## ✅ 配置测试结果

**本地配置测试已通过:**
- ✅ Creem.io正式API密钥: `creem_6AIW9sH8lsSGaAABHgfdJl`
- ✅ Basic产品ID: `prod_7GCAq6iP6E27GOwil4gfDU`
- ✅ Premium产品ID: `prod_2kqnPDGAScR6Ocf6ujtGi`
- ✅ 测试模式已关闭: `CREEM_TEST_MODE=False`
- ✅ API连接测试成功: 两个产品都能正常创建checkout

## 🚀 AWS服务器部署步骤

### 步骤1: 连接到AWS服务器

```bash
# 连接到AWS服务器 (offerott.com)
ssh -i your-key.pem ubuntu@3.138.194.143
```

### 步骤2: 上传最新代码

```bash
# 方法A: 如果服务器上已有代码，直接更新
cd /path/to/InterviewPro
git pull origin main

# 方法B: 如果需要重新克隆
git clone https://github.com/your-repo/InterviewPro.git
cd InterviewPro
```

### 步骤3: 复制配置文件

将以下文件复制到服务器：
- `production.env` - 生产环境配置
- `docker-compose.prod.yml` - 已更新的Docker配置
- `deploy_to_aws_production.sh` - 部署脚本

### 步骤4: 执行部署

```bash
# 给部署脚本执行权限
chmod +x deploy_to_aws_production.sh

# 执行部署
./deploy_to_aws_production.sh
```

## 📋 部署后验证清单

### 1. 检查服务状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 2. 检查后端日志
```bash
docker-compose -f docker-compose.prod.yml logs backend | grep -i creem
```

### 3. 测试API端点
```bash
# 测试计划获取
curl https://offerott.com/api/v1/billing/plans

# 测试回调URL (应返回400，正常)
curl https://offerott.com/api/v1/billing/callback?test=1
```

### 4. 检查配置是否生效
```bash
# 进入后端容器检查环境变量
docker-compose -f docker-compose.prod.yml exec backend env | grep CREEM
```

## 🔧 Creem.io控制台配置

### 1. 登录Creem.io控制台
- 使用与API密钥 `creem_6AIW9sH8lsSGaAABHgfdJl` 对应的账户登录

### 2. 配置Webhook
**重要**: 在Creem.io控制台中配置以下webhook设置：

```
Webhook URL: https://offerott.com/api/v1/billing/callback
HTTP Method: GET
Events: 
  - checkout.completed
  - payment.completed
  - payment.failed
```

### 3. 验证产品配置
确认以下产品在控制台中存在且配置正确：
- Basic计划: `prod_7GCAq6iP6E27GOwil4gfDU`
- Premium计划: `prod_2kqnPDGAScR6Ocf6ujtGi`

## 🧪 支付流程测试

### 1. 访问支付页面
```
https://offerott.com/billing
```

### 2. 测试支付流程
1. 选择Basic或Premium计划
2. 点击购买按钮
3. 完成支付流程
4. 检查是否正确重定向到成功页面

### 3. 验证回调
```bash
# 实时查看回调日志
docker-compose -f docker-compose.prod.yml logs -f backend | grep "PAYMENT CALLBACK"
```

### 4. 检查数据库状态
```bash
# 进入MySQL容器检查订单状态
docker-compose -f docker-compose.prod.yml exec mysql mysql -u user -p interviewpro

# 查询最新支付记录
SELECT * FROM payment_history ORDER BY created_at DESC LIMIT 5;

# 查询订阅状态
SELECT * FROM subscriptions ORDER BY updated_at DESC LIMIT 5;
```

## 📊 预期结果

### 成功指标
- ✅ 使用正式Creem API: `https://api.creem.io`
- ✅ 回调URL稳定: `https://offerott.com/api/v1/billing/callback`
- ✅ 支付成功后状态变为: `completed`
- ✅ 订阅正确激活
- ✅ 回调成功率: 95%+

### 回调成功的标志
在日志中看到类似信息：
```
🔔 PAYMENT CALLBACK RECEIVED AT 2025-01-28 21:xx:xx
✅ Subscription update successful
🎉 Successfully updated subscription for user X to plan basic/premium
```

## 🛠️ 故障排除

### 如果回调仍然失败

1. **检查Creem.io控制台**
   - Webhook发送历史
   - 错误日志和重试记录

2. **检查服务器防火墙**
   ```bash
   sudo ufw status
   sudo ufw allow 80
   sudo ufw allow 443
   ```

3. **检查SSL证书**
   ```bash
   curl -I https://offerott.com/api/v1/billing/callback
   ```

4. **检查Nginx配置**
   ```bash
   docker-compose -f docker-compose.prod.yml logs nginx
   ```

## 📈 预期改善

| 指标 | 当前 (测试+本地) | 部署后 (正式+服务器) |
|------|------------------|---------------------|
| **回调成功率** | 15-20% | 95%+ |
| **API稳定性** | 测试环境 | 生产环境 |
| **网络稳定性** | ngrok (不稳定) | 固定域名 |
| **支付体验** | 经常失败 | 稳定可靠 |

## 🎯 关键配置对比

### 修改前 (测试环境)
```bash
CREEM_TEST_MODE=True
CREEM_API_KEY=creem_test_3sd9xtWYIYo1226oBRWBoZ
API_URL=https://test-api.creem.io/v1/checkouts
CALLBACK_URL=https://xxxx.ngrok-free.app/api/v1/billing/callback
```

### 修改后 (生产环境)
```bash
CREEM_TEST_MODE=False
CREEM_API_KEY=creem_6AIW9sH8lsSGaAABHgfdJl
API_URL=https://api.creem.io/v1/checkouts
CALLBACK_URL=https://offerott.com/api/v1/billing/callback
```

## ✅ 部署完成检查清单

- [ ] AWS服务器连接正常
- [ ] 代码已更新到最新版本
- [ ] Docker服务启动成功
- [ ] 环境变量配置正确
- [ ] API端点响应正常
- [ ] Creem.io控制台webhook已配置
- [ ] 支付流程测试通过
- [ ] 回调日志显示成功

**完成以上所有步骤后，回调问题应该得到彻底解决！**
