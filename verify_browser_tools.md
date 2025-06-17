# 🛠️ Browser-tools MCP工具验证设置指南

## ✅ 已完成的配置步骤

### 1. MCP配置文件更新 ✅
- 文件位置: `~/.cursor/mcp.json`
- 配置类型: 使用正确的 `@agentdeskai/browser-tools-mcp@1.2.0`
- 移除了错误的环境变量配置

### 2. 服务器启动状态 ✅
两个必需的服务器都在运行:
- **browser-tools-server**: 中间件服务器 (进程ID: 15676)
- **browser-tools-mcp**: MCP服务器 (进程ID: 15581)

## 🔧 下一步需要完成的步骤

### 3. 安装Chrome扩展 📋
需要安装BrowserTools Chrome扩展:

1. 下载扩展: [v1.2.0 BrowserToolsMCP Chrome Extension](https://github.com/AgentDeskAI/browser-tools-mcp/releases)
2. 解压扩展文件
3. 在Chrome中加载开发者模式扩展:
   - 打开 `chrome://extensions/`
   - 启用"开发者模式"
   - 点击"加载已解压的扩展程序"
   - 选择解压后的扩展文件夹

### 4. 重启Cursor ⚠️
配置更改后需要完全重启Cursor:
1. 完全退出Cursor (不仅仅是关闭窗口)
2. 在Activity Monitor中确认Cursor进程已终止
3. 重新启动Cursor
4. 检查 Settings > MCP 查看browser-tools是否显示

## 🎯 验证MCP工具可用性

重启Cursor后，您应该能够看到以下browser-tools工具:

### 可用工具列表:
- `captureScreenshot` - 捕获浏览器截图
- `getConsoleLogs` - 获取控制台日志
- `getNetworkLogs` - 获取网络请求日志
- `getSelectedElement` - 获取选中的DOM元素
- `clearLogs` - 清除日志
- `runAccessibilityAudit` - 运行可访问性审计
- `runPerformanceAudit` - 运行性能审计
- `runSEOAudit` - 运行SEO审计
- `runBestPracticesAudit` - 运行最佳实践审计
- `runAuditMode` - 运行审计模式
- `runDebuggerMode` - 运行调试模式
- `runNextJSAudit` - 运行NextJS审计

## 🧪 测试示例

安装扩展并重启Cursor后，您可以测试以下命令:

```
"帮我截图当前浏览器页面"
"获取浏览器控制台错误日志" 
"对当前页面运行性能审计"
"运行前端页面的可访问性检查"
```

## 📋 故障排除

如果工具仍然不可用:

1. **检查服务器状态**:
   ```bash
   ps aux | grep browser-tools
   ```

2. **检查Chrome扩展**:
   - 打开Chrome DevTools
   - 查找"BrowserToolsMCP"面板
   - 确认扩展与服务器连接

3. **重新安装** (如果需要):
   ```bash
   npx @agentdeskai/browser-tools-server@1.2.0
   ```

## 🎉 配置状态总结

- ✅ MCP配置文件已更新
- ✅ browser-tools-server 运行中
- ✅ browser-tools-mcp 运行中  
- 📋 需要: 安装Chrome扩展
- 📋 需要: 重启Cursor

一旦完成剩余步骤，browser-tools MCP工具就应该完全可用了！ 