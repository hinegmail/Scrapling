# Scrapling Web UI - Frontend

React 18+ TypeScript 前端应用，为 Scrapling Web UI 提供用户界面。

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── main.tsx              # 应用入口
│   ├── App.tsx               # 主应用组件
│   ├── index.css             # 全局样式
│   ├── pages/                # 页面组件
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── TasksPage.tsx
│   │   ├── ResultsPage.tsx
│   │   └── HistoryPage.tsx
│   ├── components/           # 可复用组件
│   │   ├── Layout.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── common/
│   ├── hooks/                # 自定义 Hooks
│   │   ├── useAuth.ts
│   │   ├── useTask.ts
│   │   └── useWebSocket.ts
│   ├── store/                # Redux 存储
│   │   ├── index.ts
│   │   ├── authSlice.ts
│   │   ├── taskSlice.ts
│   │   └── uiSlice.ts
│   ├── services/             # API 服务
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── types/                # TypeScript 类型
│   │   ├── index.ts
│   │   ├── auth.ts
│   │   └── task.ts
│   └── utils/                # 工具函数
│       ├── constants.ts
│       └── helpers.ts
├── public/                   # 静态资源
├── index.html               # HTML 模板
├── package.json             # 项目配置
├── tsconfig.json            # TypeScript 配置
├── vite.config.ts           # Vite 配置
├── tailwind.config.js       # Tailwind 配置
├── postcss.config.js        # PostCSS 配置
├── .eslintrc.json           # ESLint 配置
└── .prettierrc.json         # Prettier 配置
```

## 开发

### 代码风格

使用 Prettier 和 ESLint 进行代码格式化和检查：

```bash
# 格式化代码
npm run format

# 检查代码
npm run lint

# 类型检查
npm run type-check
```

### 测试

```bash
# 运行测试
npm run test

# 查看测试覆盖率
npm run test:coverage

# 打开测试 UI
npm run test:ui
```

## 部署

参考 `Dockerfile` 进行 Docker 部署。
