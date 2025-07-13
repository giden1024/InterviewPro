# OAuth 第三方登录设置指南

## 概述
此功能已为 OfferOtter 应用添加了 Google 和 Facebook 第三方登录功能。用户可以通过点击登录页面的按钮直接跳转到相应的第三方平台进行身份验证。

## 功能特性
- ✅ Google OAuth 2.0 登录
- ✅ Facebook OAuth 登录  
- ✅ 安全的状态验证
- ✅ 自动重定向处理
- ✅ 错误处理和用户反馈
- ✅ 回调页面处理

## 快速开始

### 1. 环境变量配置

复制 `frontend/.env.example` 文件为 `.env.local`:

```bash
cd frontend
cp .env.example .env.local
```

然后编辑 `.env.local` 文件，填入您的 OAuth 配置：

```env
# Google OAuth Client ID
VITE_GOOGLE_CLIENT_ID=your-actual-google-client-id

# Facebook App ID  
VITE_FACEBOOK_APP_ID=your-actual-facebook-app-id

# OAuth Redirect URI
VITE_OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback
```

### 2. Google OAuth 设置

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google+ API 或 People API
4. 创建 OAuth 2.0 客户端 ID：
   - 应用类型：Web 应用
   - 授权的重定向 URI：`http://localhost:3000/auth/callback`
5. 复制客户端 ID 到环境变量

### 3. Facebook OAuth 设置

1. 访问 [Facebook Developers](https://developers.facebook.com/)
2. 创建新应用或选择现有应用
3. 添加 Facebook Login 产品
4. 配置有效的 OAuth 重定向 URI：`http://localhost:3000/auth/callback`
5. 复制 App ID 到环境变量

## 使用方法

### 前端使用

在登录页面 (`http://localhost:3000/login`)，用户可以：

1. 点击 **"Continue with Google"** 按钮
   - 自动跳转到 Google 授权页面
   - 用户同意授权后返回应用
   - 自动完成登录并跳转到主页

2. 点击 **"Continue with Facebook"** 按钮
   - 自动跳转到 Facebook 授权页面
   - 用户同意授权后返回应用
   - 自动完成登录并跳转到主页

### 技术实现

#### OAuth 服务 (`frontend/src/services/oauthService.ts`)
- `initiateGoogleLogin()`: 启动 Google OAuth 流程
- `initiateFacebookLogin()`: 启动 Facebook OAuth 流程
- `handleCallback()`: 处理 OAuth 回调
- `parseCallbackUrl()`: 解析回调 URL 参数

#### 回调页面 (`frontend/src/pages/OAuthCallbackPage.tsx`)
- 处理来自第三方平台的授权回调
- 验证状态参数防止 CSRF 攻击
- 显示登录状态（加载中、成功、失败）
- 自动重定向到相应页面

#### 路由配置
- `/auth/callback`: OAuth 回调处理页面

## 安全特性

1. **状态验证**: 使用随机生成的 state 参数防止 CSRF 攻击
2. **会话存储**: 安全地存储临时状态信息
3. **错误处理**: 完善的错误捕获和用户反馈
4. **参数验证**: 严格验证回调参数的完整性

## 生产环境部署

### 域名配置
在生产环境中，需要更新以下配置：

1. **环境变量**:
```env
VITE_OAUTH_REDIRECT_URI=https://yourdomain.com/auth/callback
```

2. **Google Cloud Console**:
   - 添加生产域名到授权重定向 URI
   - 更新 JavaScript 源

3. **Facebook Developer Console**:
   - 添加生产域名到有效 OAuth 重定向 URI
   - 更新应用域名

### SSL 证书
确保生产环境使用 HTTPS，第三方 OAuth 服务通常要求安全连接。

## 故障排除

### 常见问题

1. **"Invalid redirect URI"**
   - 检查环境变量配置
   - 确认第三方平台的重定向 URI 设置

2. **"Invalid client ID"**
   - 验证客户端 ID 是否正确
   - 确认 API 是否已启用

3. **"State parameter mismatch"**
   - 检查浏览器是否允许 sessionStorage
   - 确认没有多个标签页并发操作

### 调试模式

查看浏览器控制台日志，OAuth 服务会输出详细的调试信息：

```javascript
// 在浏览器控制台查看
console.log('OAuth redirect URL:', googleAuthUrl.toString());
console.log('Processing OAuth callback:', { provider, hasCode: !!code });
```

## API 接口（后端集成）

前端会调用后端 OAuth 回调接口：

```typescript
POST /api/auth/oauth/callback
{
  "code": "authorization_code",
  "state": "random_state",
  "provider": "google" | "facebook",
  "redirect_uri": "callback_url"
}
```

后端需要实现此接口来：
1. 验证授权码
2. 获取用户信息
3. 创建或更新用户账户
4. 返回访问令牌

## 测试

### 开发环境测试
1. 启动前端服务：`npm run dev`
2. 访问：`http://localhost:3000/login`
3. 点击第三方登录按钮测试

### 功能测试清单
- [ ] Google 登录按钮跳转正常
- [ ] Facebook 登录按钮跳转正常
- [ ] 授权成功后正确返回
- [ ] 错误情况正确处理
- [ ] 用户信息正确获取
- [ ] 登录状态正确保持

## 更新日志

### v1.0.0 (当前版本)
- ✅ 实现 Google OAuth 2.0 集成
- ✅ 实现 Facebook OAuth 集成
- ✅ 添加回调页面处理
- ✅ 完善错误处理机制
- ✅ 添加安全状态验证

## 技术支持

如果在配置或使用过程中遇到问题，请检查：
1. 环境变量是否正确配置
2. 第三方平台配置是否完整
3. 网络连接是否正常
4. 浏览器控制台是否有错误信息 