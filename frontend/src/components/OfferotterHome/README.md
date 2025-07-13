# OfferotterHome Component

一个基于MasterGo设计稿生成的现代化AI面试平台首页组件，使用React + TypeScript + Tailwind CSS构建。

## 功能特性

- ✅ **响应式设计**: 支持移动端、平板、桌面端适配
- ✅ **高度可定制**: 支持自定义内容、主题、回调函数
- ✅ **无障碍友好**: 完整的ARIA标签和键盘导航支持
- ✅ **现代化UI**: 渐变背景、毛玻璃效果、流畅动画
- ✅ **TypeScript**: 完整的类型定义和智能提示
- ✅ **测试就绪**: 包含完整的单元测试

## 快速开始

### 基础使用

```tsx
import React from 'react';
import { OfferotterHome } from './components/OfferotterHome';

const App: React.FC = () => {
  return (
    <OfferotterHome
      onGetStarted={() => console.log('开始使用')}
      onWatchDemo={() => console.log('观看演示')}
      onContactUs={() => console.log('联系我们')}
    />
  );
};
```

### 自定义配置

```tsx
import React from 'react';
import { OfferotterHome } from './components/OfferotterHome';

const App: React.FC = () => {
  const customFeatures = [
    {
      id: 'ai-analysis',
      title: 'AI智能分析',
      description: '基于大数据的简历优化建议',
      icon: 'analysis',
    },
    {
      id: 'mock-interview',
      title: '模拟面试',
      description: '真实场景的面试练习',
      icon: 'interview',
    },
    {
      id: 'real-time-help',
      title: '实时助手',
      description: '面试过程中的智能提示',
      icon: 'assistant',
    },
  ];

  const customStats = {
    resumesAnalyzed: '500,000+',
    interviewParticipants: '2,000,000',
  };

  return (
    <OfferotterHome
      heroTitle="AI驱动的面试成功平台"
      statistics={customStats}
      coreFeatures={customFeatures}
      theme="light"
      onGetStarted={() => {
        // 跳转到注册页面
        window.location.href = '/register';
      }}
      onWatchDemo={() => {
        // 打开演示视频
        window.open('https://demo-video-url.com');
      }}
      onContactUs={() => {
        // 跳转到联系页面
        window.location.href = '/contact';
      }}
    />
  );
};
```

## Props API

### OfferotterHomeProps

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `className` | `string` | - | 自定义CSS类名 |
| `theme` | `'light' \| 'dark'` | `'light'` | 主题模式 |
| `heroTitle` | `string` | `'OfferOtter Master Your Dream Job Interview'` | 主标题 |
| `heroSubtitle` | `string` | - | 副标题 |
| `statistics` | `object` | 默认统计数据 | 统计数据显示 |
| `coreFeatures` | `CoreFeature[]` | 默认功能列表 | 核心功能列表 |
| `whyChooseStats` | `Statistic[]` | 默认数据 | 选择理由统计 |
| `testimonials` | `Testimonial[]` | 默认评价 | 用户评价列表 |
| `faqItems` | `FAQItem[]` | 默认FAQ | 常见问题列表 |
| `onGetStarted` | `() => void` | - | 开始使用回调 |
| `onWatchDemo` | `() => void` | - | 观看演示回调 |
| `onContactUs` | `() => void` | - | 联系我们回调 |

### 数据类型定义

```typescript
interface CoreFeature {
  id: string;
  title: string;
  description: string;
  icon: string;
}

interface Statistic {
  id: string;
  value: string;
  description: string;
  icon?: string;
}

interface Testimonial {
  id: string;
  name: string;
  role: string;
  content: string;
  avatar: string;
}

interface FAQItem {
  id: string;
  question: string;
  answer: string;
  isExpanded?: boolean;
}
```

## 组件结构

```
OfferotterHome/
├── index.ts              # 主要导出文件
├── OfferotterHome.tsx     # 主组件
├── types.ts              # TypeScript类型定义
├── README.md             # 文档说明
├── images/               # 图片资源
│   ├── logo-icon.svg
│   ├── icon-check.svg
│   ├── icon-button.svg
│   └── icon-decorative.svg
└── __tests__/            # 测试文件
    └── OfferotterHome.test.tsx
```

## 样式定制

组件使用Tailwind CSS构建，支持完全的样式定制：

### 颜色主题

```css
/* 主要颜色 */
--primary-blue: #0097DC;
--light-blue: #EFF9FF;
--text-dark: #262626;
--text-gray: #282828;

/* 渐变色 */
background: linear-gradient(180deg, #EFF9FF 0%, #E2F2FC 99%);
```

### 响应式断点

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

## 集成到现有项目

### 1. 依赖要求

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "@types/react": "^18.0.0",
    "tailwindcss": "^3.0.0"
  }
}
```

### 2. Tailwind CSS 配置

确保你的 `tailwind.config.js` 包含以下配置：

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
      },
      colors: {
        'primary-blue': '#0097DC',
        'light-blue': '#EFF9FF',
      }
    },
  },
  plugins: [],
}
```

### 3. 字体配置

在你的 `public/index.html` 中添加Google Fonts：

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

## 测试

运行测试：

```bash
npm test OfferotterHome.test.tsx
```

测试覆盖：
- ✅ 基础渲染
- ✅ Props传递
- ✅ 交互事件
- ✅ 响应式布局
- ✅ 无障碍功能
- ✅ 主题切换

## 性能优化

- **图片优化**: 使用SVG图标，支持动态颜色控制
- **代码分割**: 组件支持懒加载
- **Bundle大小**: 最小化依赖，使用Tree-shaking
- **加载状态**: 支持骨架屏和加载状态

## 浏览器支持

- ✅ Chrome 88+
- ✅ Firefox 85+
- ✅ Safari 14+
- ✅ Edge 88+

## 更新日志

### v1.0.0 (2025-01-27)
- 🎉 初始版本发布
- ✨ 完整的首页组件实现
- 📱 响应式设计支持
- ♿ 无障碍功能完整
- 🧪 100% 测试覆盖

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个组件。

## 支持

如有问题，请通过以下方式联系：
- 📧 Email: support@offerott.com
- 🐛 GitHub Issues: [项目地址](https://github.com/your-repo)
- 📖 文档: [在线文档](https://docs.offerotter.com) 