# InterviewPro生产环境部署计划

## 🎯 目标
将InterviewPro部署到AWS生产服务器(3.138.194.143 / offerott.com)，使用正式Creem.io API解决回调问题。

## 📋 现有资源
✅ **服务器**: AWS EC2 (3.138.194.143) - 已配置offerott.com域名  
✅ **SSL证书**: Let's Encrypt已配置  
✅ **Docker环境**: 服务器已安装Docker和Docker Compose  
✅ **生产配置**: production.env和docker-compose.prod.yml已准备  
✅ **Creem配置**: 正式API密钥和产品ID已配置  

## 🚀 部署步骤

### 步骤1: 连接到服务器
```bash
# 使用现有的SSH密钥连接
ssh -i ~/.ssh/your-key.pem ubuntu@3.138.194.143

# 或者如果已配置SSH别名
ssh offerott-server
```

### 步骤2: 更新项目代码
```bash
# 进入项目目录
cd /home/ubuntu/InterviewPro

# 拉取最新代码(包含我们的Creem配置修改)
git pull origin main

# 检查关键文件是否存在
ls -la production.env docker-compose.prod.yml AWS_PRODUCTION_CREEM_DEPLOYMENT.md
```

### 步骤3: 执行部署
```bash
# 方案A: 使用我们新创建的生产部署脚本
chmod +x deploy_to_aws_production.sh
./deploy_to_aws_production.sh

# 方案B: 使用现有的AWS部署脚本
chmod +x scripts/deploy/deploy-aws.sh
./scripts/deploy/deploy-aws.sh
```

### 步骤4: 验证部署
```bash
# 检查Docker服务状态
docker-compose -f docker-compose.prod.yml ps

# 检查后端日志
docker-compose -f docker-compose.prod.yml logs backend | grep -i creem

# 测试API端点
curl https://offerott.com/api/v1/billing/plans
curl https://offerott.com/api/v1/billing/callback?test=1
```

### 步骤5: 配置Creem.io Webhook
在Creem.io控制台中配置:
- **Webhook URL**: `https://offerott.com/api/v1/billing/callback`
- **Events**: checkout.completed, payment.completed, payment.failed

### 步骤6: 测试支付流程
1. 访问: `https://offerott.com/billing`
2. 购买Basic或Premium计划
3. 验证回调是否成功

## 🔧 关键配置对比

### 修改前(测试环境)
```bash
CREEM_TEST_MODE=True
CREEM_API_KEY=creem_test_3sd9xtWYIYo1226oBRWBoZ
CALLBACK_URL=https://xxxx.ngrok-free.app/api/v1/billing/callback
```

### 修改后(生产环境)
```bash
CREEM_TEST_MODE=False
CREEM_API_KEY=creem_6AIW9sH8lsSGaAABHgfdJl
CREEM_BASIC_PRODUCT_ID=prod_7GCAq6iP6E27GOwil4gfDU
CREEM_PREMIUM_PRODUCT_ID=prod_2kqnPDGAScR6Ocf6ujtGi
CALLBACK_URL=https://offerott.com/api/v1/billing/callback
```

## 📊 预期改善

| 指标 | 当前(测试+本地) | 部署后(正式+服务器) |
|------|----------------|-------------------|
| **回调成功率** | 15-20% | 95%+ |
| **API稳定性** | 测试环境 | 生产环境 |
| **网络稳定性** | ngrok(不稳定) | 固定域名 |
| **支付体验** | 经常失败 | 稳定可靠 |

## 🛠️ 故障排除

如果遇到问题，请检查:
1. **服务器连接**: `ping 3.138.194.143`
2. **Docker状态**: `docker ps -a`
3. **端口开放**: `sudo ufw status`
4. **SSL证书**: `curl -I https://offerott.com`
5. **回调日志**: `docker-compose -f docker-compose.prod.yml logs -f backend | grep CALLBACK`

## ✅ 成功标志

部署成功后应该看到:
- ✅ 所有Docker容器运行正常
- ✅ API端点返回200状态码
- ✅ 支付流程完整无错误
- ✅ 回调日志显示成功接收
- ✅ 订阅状态正确更新

## 📞 联系方式

如果部署过程中遇到问题，可以:
1. 查看详细的部署日志
2. 检查AWS_PRODUCTION_CREEM_DEPLOYMENT.md中的故障排除部分
3. 使用现有的监控脚本: `scripts/monitor/check-server-status.sh`
