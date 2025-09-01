# 🎯 InterviewPro 付费功能使用指南

## ✅ **问题已解决**

**导入错误已修复**: `billingService.ts` 中的 API 导入问题已解决

## 🚀 **正确的访问地址**

- **前端服务**: http://localhost:3001 (不是3000)
- **后端服务**: http://localhost:5001
- **付费页面**: **http://localhost:3001/billing**

## 📋 **完整测试流程**

### **步骤1: 用户注册/登录**
1. 访问: http://localhost:3001/login
2. 注册新用户或使用现有账号登录
3. 登录成功后会自动获得免费订阅

### **步骤2: 查看付费页面**
1. 访问: http://localhost:3001/billing
2. 查看三个付费计划:
   - **免费版**: ¥0/月 (3次面试，10个AI问题)
   - **基础版**: ¥29/月 (20次面试，100个AI问题，语音功能)
   - **高级版**: ¥99/月 (无限使用，所有高级功能)

### **步骤3: 测试支付流程**
1. 点击"升级到基础版"或"升级到高级版"
2. 系统会跳转到Creem.io测试支付页面
3. 在测试环境中完成支付
4. 支付成功后回调到系统更新订阅状态

## 🧪 **Creem.io 测试配置**

- **API Key**: `creem_test_3sd9xtWYIYo1226oBRWBoZ`
- **Product ID**: `prod_1UsU2rK5AiyVINJuHWnPyy`
- **测试模式**: ✅ 已启用
- **支付测试**: 可以使用测试卡号进行支付

## 🔧 **技术状态**

### **服务运行状态**
- ✅ 后端API服务正常 (端口5001)
- ✅ 前端React服务正常 (端口3001)
- ✅ 数据库表已创建
- ✅ 付费API端点正常工作

### **API端点测试**
```bash
# 测试付费计划API
curl http://localhost:5001/api/v1/billing/plans

# 测试认证端点（需要登录）
curl http://localhost:5001/api/v1/billing/subscription
```

## 🎯 **功能特性**

### **付费计划对比**
| 功能 | 免费版 | 基础版 | 高级版 |
|------|--------|--------|--------|
| 面试次数/月 | 3次 | 20次 | 无限 |
| AI问题/月 | 10个 | 100个 | 无限 |
| 简历分析/月 | 1次 | 5次 | 无限 |
| 历史记录 | 7天 | 30天 | 365天 |
| 语音面试 | ❌ | ✅ | ✅ |
| 自定义问题 | ❌ | ❌ | ✅ |
| 高级分析 | ❌ | ❌ | ✅ |

### **权限控制**
系统会自动：
- 检查用户订阅状态
- 限制功能使用次数
- 在达到限制时提示升级
- 处理订阅到期和续费

## 🛠️ **开发者信息**

### **前端组件**
- `BillingPage.tsx` - 主付费页面
- `PricingPlans.tsx` - 付费计划展示
- `SubscriptionStatus.tsx` - 订阅状态管理
- `billingService.ts` - API服务层

### **后端API**
- `/api/v1/billing/plans` - 获取付费计划
- `/api/v1/billing/subscription` - 用户订阅状态
- `/api/v1/billing/checkout` - 创建支付会话
- `/api/v1/billing/callback` - 支付回调处理

### **数据库表**
- `subscriptions` - 用户订阅信息
- `payment_history` - 支付历史记录

## 🎉 **立即开始测试**

1. **访问主页**: http://localhost:3001/
2. **注册账号**: http://localhost:3001/register
3. **查看付费**: http://localhost:3001/billing
4. **测试支付**: 选择付费计划进行升级

---

**所有功能都已配置完成，可以开始完整的付费功能测试！** 🚀

如有任何问题，请检查：
- 浏览器控制台是否有JavaScript错误
- 网络请求是否正常
- 后端服务是否正在运行
