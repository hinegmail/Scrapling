# Scrapling Web UI 设计文档

## Overview

Scrapling Web UI 是一个现代化的全栈 Web 应用，为非技术用户提供图形化界面来使用 Scrapling 高性能网页爬取框架。该系统通过浏览器提供直观的爬虫任务管理、实时进度监控和可视化结果展示。

### 设计目标

1. **易用性**：非技术用户可以无需编写代码即可创建和执行爬虫任务
2. **实时性**：通过 WebSocket 提供实时进度更新和日志流
3. **可靠性**：支持任务暂停/恢复、错误恢复和数据持久化
4. **可扩展性**：支持多并发用户和大规模数据处理
5. **安全性**：完整的身份验证、授权和数据加密

### 核心功能

- 用户认证与会话管理
- 爬虫任务创建、配置和执行
- 实时进度监控和日志查看
- 结果数据展示、搜索和导出
- 任务历史管理和重复使用
- 获取器选择与参数配置
- 选择器验证与预览
- 代理和请求头管理
- 仪表板与统计分析
- 错误处理与恢复建议

## Architecture

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Web UI (TypeScript)                               │   │
│  │  - Pages: Login, Dashboard, Tasks, Results, History      │   │
│  │  - Components: Forms, Tables, Charts, Modals             │   │
│  │  - State Management: Redux/Zustand                       │   │
│  │  - Styling: Tailwind CSS + shadcn/ui                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                    HTTP + WebSocket                              │
│                              │                                    │
└──────────────────────────────┼────────────────────────────────────┘
                               │
┌──────────────────────────────┼────────────────────────────────────┐
│                    API Gateway / Load Balancer                    │
└──────────────────────────────┼────────────────────────────────────┘
                               │
┌──────────────────────────────┼────────────────────────────────────┐
│                         Application Layer                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend (Python 3.10+)                          │   │
│  │  - REST API Endpoints (Task, Result, User, Auth)         │   │
│  │  - WebSocket Handlers (Progress, Logs)                   │   │
│  │  - Business Logic & Validation                           │   │
│  │  - Middleware (Auth, CORS, Rate Limiting)                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                    ┌─────────┼─────────┐                         │
│                    │         │         │                         │
│  ┌─────────────────▼──┐  ┌──▼──────┐  │                         │
│  │  Scrapling Engine  │  │  Task   │  │                         │
│  │  - Fetchers        │  │  Queue  │  │                         │
│  │  - Parsers         │  │  (Celery)  │                         │
│  │  - Spiders         │  └─────────┘  │                         │
│  └────────────────────┘               │                         │
│                                       │                         │
│                    ┌──────────────────▼──┐                      │
│                    │  WebSocket Manager   │                      │
│                    │  (Real-time Updates) │                      │
│                    └─────────────────────┘                       │
└──────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼────────────────────────────────────┐
│                         Data Layer                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                     │   │
│  │  - Users, Sessions, Tasks, Results, Logs                │   │
│  │  - Indexes for Performance                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Redis Cache                                             │   │
│  │  - Session Cache, Task Status, Rate Limiting            │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 技术栈

**前端**：
- React 18+ with TypeScript
- Redux Toolkit / Zustand (状态管理)
- Tailwind CSS + shadcn/ui (UI 组件库)
- Axios (HTTP 客户端)
- Socket.io-client (WebSocket)
- Recharts (数据可视化)
- React Router (路由)

**后端**：
- FastAPI (Web 框架)
- SQLAlchemy (ORM)
- Pydantic (数据验证)
- Celery (任务队列)
- python-socketio (WebSocket)
- PyJWT (身份验证)
- Scrapling (爬虫框架)

**数据库**：
- PostgreSQL (主数据库)
- Redis (缓存和会话存储)

**部署**：
- Docker & Docker Compose
- Nginx (反向代理)
- Gunicorn (WSGI 服务器)
- Supervisor (进程管理)

## Components and Interfaces

### 前端组件架构

```
App
├── Layout
│   ├── Header (导航、用户菜单)
│   ├── Sidebar (菜单导航)
│   └── Footer
├── Pages
│   ├── LoginPage
│   ├── DashboardPage
│   │   ├── StatisticsCard
│   │   ├── TrendChart
│   │   ├── FetcherPieChart
│   │   └── ResourceMonitor
│   ├── TasksPage
│   │   ├── TaskList
│   │   ├── TaskForm
│   │   ├── FetcherSelector
│   │   ├── SelectorValidator
│   │   └── AdvancedOptions
│   ├── TaskDetailPage
│   │   ├── ProgressMonitor
│   │   ├── LogViewer
│   │   ├── ControlPanel (暂停/恢复/停止)
│   │   └── StatusDisplay
│   ├── ResultsPage
│   │   ├── ResultTable
│   │   ├── ResultDetail
│   │   ├── ExportDialog
│   │   └── SearchFilter
│   ├── HistoryPage
│   │   ├── TaskHistoryList
│   │   ├── TaskFilter
│   │   └── BulkActions
│   ├── SettingsPage
│   │   ├── ProxyManager
│   │   ├── HeaderManager
│   │   ├── CookieImporter
│   │   └── PreferenceSettings
│   └── HelpPage
│       ├── Documentation
│       ├── FAQ
│       └── VideoTutorials
├── Modals
│   ├── ConfirmDialog
│   ├── ErrorDialog
│   ├── SuccessNotification
│   └── LoadingSpinner
└── Hooks
    ├── useAuth
    ├── useTask
    ├── useWebSocket
    ├── useNotification
    └── useLocalStorage
```

### 后端 API 端点

#### 认证相关

```
POST   /api/v1/auth/register          - 用户注册
POST   /api/v1/auth/login             - 用户登录
POST   /api/v1/auth/logout            - 用户登出
POST   /api/v1/auth/refresh           - 刷新 JWT 令牌
GET    /api/v1/auth/me                - 获取当前用户信息
POST   /api/v1/auth/change-password   - 修改密码
```

#### 任务管理

```
GET    /api/v1/tasks                  - 获取任务列表（分页、过滤）
POST   /api/v1/tasks                  - 创建新任务
GET    /api/v1/tasks/{task_id}        - 获取任务详情
PUT    /api/v1/tasks/{task_id}        - 更新任务配置
DELETE /api/v1/tasks/{task_id}        - 删除任务
POST   /api/v1/tasks/{task_id}/run    - 执行任务
POST   /api/v1/tasks/{task_id}/pause  - 暂停任务
POST   /api/v1/tasks/{task_id}/resume - 恢复任务
POST   /api/v1/tasks/{task_id}/stop   - 停止任务
POST   /api/v1/tasks/{task_id}/clone  - 复制任务
```

#### 结果管理

```
GET    /api/v1/tasks/{task_id}/results           - 获取任务结果（分页）
GET    /api/v1/tasks/{task_id}/results/{result_id} - 获取单个结果详情
POST   /api/v1/tasks/{task_id}/results/export    - 导出结果（CSV/JSON/Excel）
GET    /api/v1/tasks/{task_id}/results/search    - 搜索结果
```

#### 选择器验证

```
POST   /api/v1/selectors/validate     - 验证选择器语法
POST   /api/v1/selectors/test         - 测试选择器（获取匹配元素）
POST   /api/v1/selectors/preview      - 获取网页预览
```

#### 配置管理

```
GET    /api/v1/config/proxies         - 获取代理列表
POST   /api/v1/config/proxies         - 添加代理
PUT    /api/v1/config/proxies/{id}    - 更新代理
DELETE /api/v1/config/proxies/{id}    - 删除代理

GET    /api/v1/config/headers         - 获取自定义请求头
POST   /api/v1/config/headers         - 添加请求头
PUT    /api/v1/config/headers/{id}    - 更新请求头
DELETE /api/v1/config/headers/{id}    - 删除请求头

POST   /api/v1/config/cookies/import  - 导入 Cookie
```

#### 仪表板

```
GET    /api/v1/dashboard/statistics   - 获取统计信息
GET    /api/v1/dashboard/trends       - 获取趋势数据
GET    /api/v1/dashboard/resources    - 获取资源使用情况
```

#### 日志与监控

```
GET    /api/v1/logs/tasks/{task_id}   - 获取任务日志
GET    /api/v1/logs/system            - 获取系统日志
GET    /api/v1/health                 - 健康检查
```

### WebSocket 事件

#### 客户端发送事件

```
connect                    - 连接到 WebSocket
disconnect                 - 断开连接
subscribe_task            - 订阅任务进度更新
unsubscribe_task          - 取消订阅任务
```

#### 服务器推送事件

```
task_started              - 任务开始
task_progress             - 任务进度更新
  {
    task_id: string,
    processed_count: number,
    total_count: number,
    success_count: number,
    error_count: number,
    current_url: string,
    elapsed_time: number,
    estimated_remaining: number
  }

task_log                  - 新日志消息
  {
    task_id: string,
    level: "INFO" | "WARNING" | "ERROR",
    message: string,
    timestamp: ISO8601
  }

task_completed            - 任务完成
  {
    task_id: string,
    status: "success" | "failed" | "stopped",
    total_time: number,
    results_count: number,
    error_message?: string
  }

task_paused               - 任务暂停
task_resumed              - 任务恢复
task_stopped              - 任务停止
```

## Data Models

### 用户模型

```python
class User(Base):
    id: UUID
    username: str (unique, indexed)
    email: str (unique, indexed)
    password_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime
    
    # 关系
    tasks: List[Task]
    sessions: List[Session]
```

### 会话模型

```python
class Session(Base):
    id: UUID
    user_id: UUID (FK)
    token: str (unique, indexed)
    expires_at: datetime
    created_at: datetime
    ip_address: str
    user_agent: str
    
    # 关系
    user: User
```

### 任务模型

```python
class Task(Base):
    id: UUID
    user_id: UUID (FK)
    name: str
    description: str
    target_url: str
    fetcher_type: Enum["http", "dynamic", "stealthy"]
    selector: str (CSS or XPath)
    selector_type: Enum["css", "xpath"]
    timeout: int (seconds)
    retry_count: int
    status: Enum["draft", "running", "paused", "completed", "failed", "stopped"]
    
    # 高级选项
    use_proxy_rotation: bool
    solve_cloudflare: bool
    custom_headers: JSON
    cookies: JSON
    
    # 浏览器配置（动态获取器）
    wait_time: int
    viewport_width: int
    viewport_height: int
    
    # 统计信息
    created_at: datetime
    updated_at: datetime
    last_run_at: datetime
    total_runs: int
    success_count: int
    error_count: int
    
    # 关系
    user: User
    results: List[Result]
    logs: List[TaskLog]
    proxies: List[Proxy]
```

### 结果模型

```python
class Result(Base):
    id: UUID
    task_id: UUID (FK)
    data: JSON (提取的数据)
    source_url: str
    extracted_at: datetime
    
    # 关系
    task: Task
```

### 日志模型

```python
class TaskLog(Base):
    id: UUID
    task_id: UUID (FK)
    level: Enum["DEBUG", "INFO", "WARNING", "ERROR"]
    message: str
    timestamp: datetime
    
    # 关系
    task: Task
```

### 代理模型

```python
class Proxy(Base):
    id: UUID
    user_id: UUID (FK)
    name: str
    protocol: Enum["http", "https", "socks5"]
    host: str
    port: int
    username: str (optional)
    password: str (optional, encrypted)
    is_active: bool
    created_at: datetime
    
    # 关系
    user: User
    tasks: List[Task]
```

### 数据库 ER 图

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │
│ username    │
│ email       │
│ password    │
│ is_active   │
│ created_at  │
└──────┬──────┘
       │ 1:N
       │
       ├─────────────────┬──────────────────┬──────────────────┐
       │                 │                  │                  │
       │ 1:N             │ 1:N              │ 1:N              │
       ▼                 ▼                  ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Session   │  │    Task     │  │   Proxy     │  │   Header    │
├─────────────┤  ├─────────────┤  ├─────────────┤  ├─────────────┤
│ id (PK)     │  │ id (PK)     │  │ id (PK)     │  │ id (PK)     │
│ user_id(FK) │  │ user_id(FK) │  │ user_id(FK) │  │ user_id(FK) │
│ token       │  │ name        │  │ host        │  │ key         │
│ expires_at  │  │ target_url  │  │ port        │  │ value       │
└─────────────┘  │ fetcher_type│  │ protocol    │  └─────────────┘
                 │ selector    │  │ is_active   │
                 │ status      │  │ created_at  │
                 │ created_at  │  └─────────────┘
                 └──────┬──────┘
                        │ 1:N
                        │
                 ┌──────┴──────┐
                 │             │
                 ▼ 1:N         ▼ 1:N
            ┌─────────────┐  ┌─────────────┐
            │   Result    │  │  TaskLog    │
            ├─────────────┤  ├─────────────┤
            │ id (PK)     │  │ id (PK)     │
            │ task_id(FK) │  │ task_id(FK) │
            │ data        │  │ level       │
            │ source_url  │  │ message     │
            │ extracted_at│  │ timestamp   │
            └─────────────┘  └─────────────┘
```

### 索引策略

```sql
-- 用户表
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_user_email ON users(email);

-- 会话表
CREATE INDEX idx_session_user_id ON sessions(user_id);
CREATE INDEX idx_session_token ON sessions(token);
CREATE INDEX idx_session_expires_at ON sessions(expires_at);

-- 任务表
CREATE INDEX idx_task_user_id ON tasks(user_id);
CREATE INDEX idx_task_status ON tasks(status);
CREATE INDEX idx_task_created_at ON tasks(created_at);
CREATE INDEX idx_task_user_status ON tasks(user_id, status);

-- 结果表
CREATE INDEX idx_result_task_id ON results(task_id);
CREATE INDEX idx_result_extracted_at ON results(extracted_at);

-- 日志表
CREATE INDEX idx_tasklog_task_id ON task_logs(task_id);
CREATE INDEX idx_tasklog_timestamp ON task_logs(timestamp);
CREATE INDEX idx_tasklog_level ON task_logs(level);

-- 代理表
CREATE INDEX idx_proxy_user_id ON proxies(user_id);
CREATE INDEX idx_proxy_is_active ON proxies(is_active);
```

## 正确性属性

*正确性属性是系统在所有有效执行中应该保持的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性充当人类可读规范和机器可验证的正确性保证之间的桥梁。*

### 属性 1：选择器语法验证

*对于任何* CSS 或 XPath 选择器字符串，验证系统应该根据 CSS/XPath 规范正确识别选择器语法是否有效或无效。

**验证需求：2.4, 7.1**

### 属性 2：任务配置验证

*对于任何* 具有各种必填和可选字段组合的任务配置，验证系统应该正确识别缺失的必填字段并拒绝无效配置。

**验证需求：2.5**

### 属性 3：WebSocket 进度消息完整性

*对于任何* 任务执行状态，WebSocket 进度消息应该包含所有必需字段（task_id、processed_count、total_count、success_count、error_count、current_url、elapsed_time、estimated_remaining），具有正确的数据类型和非负值。

**验证需求：3.2**

### 属性 4：结果表格分页

*对于任何* 包含 N 个项目和页面大小为 P 的结果数据集，分页应该正确地将结果分成 ceil(N/P) 页，每页包含恰好 min(P, remaining_items) 个结果。

**验证需求：4.2**

### 属性 5：数据导出格式正确性

*对于任何* 结果数据集，导出为 CSV/JSON/Excel 格式应该生成有效的文件，可以解析回来重构原始数据结构（往返属性）。

**验证需求：4.5**

### 属性 6：任务列表过滤

*对于任何* 任务列表和过滤条件（状态、日期范围、关键词），过滤结果应该只包含与所有过滤条件匹配的任务。

**验证需求：5.7**

### 属性 7：代理格式验证

*对于任何* 代理地址字符串，验证系统应该正确识别地址是否遵循有效格式（IP:port 或 hostname:port），具有有效的端口号（1-65535）。

**验证需求：8.3**

### 属性 8：代理轮换循环

*对于任何* 包含 N 个代理的列表且启用轮换，执行 N+1 个请求应该循环通过所有代理恰好一次，然后重复循环。

**验证需求：8.4**

### 属性 9：请求头 CRUD 操作

*对于任何* 自定义请求头的添加/编辑/删除操作序列，最终请求头列表应该按顺序反映所有操作，没有重复且值正确。

**验证需求：8.6**

### 属性 10：API 响应 JSON 有效性

*对于任何* 对有效端点的 API 请求，响应应该是有效的 JSON，可以解析并包含根据 API 规范的必需字段。

**验证需求：12.3**

### 属性 11：HTTP 状态码正确性

*对于任何* 错误条件（认证失败、验证错误、未找到、服务器错误），API 应该返回适当的 HTTP 状态码（分别为 401、400、404、500）。

**验证需求：12.6**

### 属性 12：输入验证安全性

*对于任何* 包含 SQL 注入或 XSS 攻击模式的用户输入，系统应该正确转义或清理输入以防止代码执行。

**验证需求：15.4**

### 属性 13：图像可访问性

*对于任何* UI 中的图像元素，图像应该有一个非空的 alt 属性来描述图像内容。

**验证需求：11.5**

## Error Handling

### 错误分类

1. **认证错误** (401)
   - 无效的凭证
   - 令牌过期
   - 权限不足

2. **验证错误** (400)
   - 无效的选择器语法
   - 缺少必填字段
   - 无效的 URL 格式

3. **资源错误** (404)
   - 任务不存在
   - 结果不存在

4. **业务逻辑错误** (422)
   - 任务状态冲突（例如，暂停已完成的任务）
   - 无效的操作序列

5. **服务器错误** (500)
   - 数据库连接失败
   - Scrapling 引擎错误
   - 未预期的异常

### 错误响应格式

```json
{
  "error": {
    "code": "INVALID_SELECTOR",
    "message": "CSS selector syntax is invalid",
    "details": {
      "selector": "div.invalid[",
      "error_position": 12
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### 错误恢复策略

1. **网络错误**：自动重试（指数退避）
2. **选择器错误**：建议修改选择器或检查网页结构
3. **Cloudflare 阻止**：建议使用隐秘获取器
4. **超时**：建议增加超时时间或使用代理
5. **数据库错误**：记录错误并通知管理员

## Testing Strategy

### 属性测试（Property-Based Testing）

根据 prework 分析，以下功能适合属性测试：

**选择器验证** (Property 1)
- 使用 fast-check 或 hypothesis 生成随机 CSS 和 XPath 选择器
- 验证验证器正确识别有效/无效语法
- 最少 100 次迭代

**任务配置验证** (Property 2)
- 生成随机任务配置，包含各种必填/可选字段组合
- 验证验证器正确识别缺失的必填字段
- 最少 100 次迭代

**WebSocket 消息完整性** (Property 3)
- 生成随机任务执行状态
- 验证 WebSocket 消息包含所有必需字段
- 验证数据类型和值范围正确
- 最少 100 次迭代

**表格分页** (Property 4)
- 生成随机大小的结果集（1-10000 项）
- 验证分页正确划分结果
- 验证每页包含正确数量的项
- 最少 100 次迭代

**数据导出格式** (Property 5)
- 生成随机结果数据集
- 导出为 CSV/JSON/Excel 格式
- 验证导出文件可以解析回原始数据结构
- 最少 100 次迭代

**任务列表过滤** (Property 6)
- 生成随机任务列表
- 应用各种过滤条件组合
- 验证过滤结果只包含匹配所有条件的任务
- 最少 100 次迭代

**代理格式验证** (Property 7)
- 生成随机代理地址字符串
- 验证验证器正确识别有效/无效格式
- 验证端口号范围检查（1-65535）
- 最少 100 次迭代

**代理轮换** (Property 8)
- 生成随机代理列表（2-10 个）
- 模拟 N+1 个请求
- 验证代理轮换循环通过所有代理
- 最少 100 次迭代

**请求头 CRUD** (Property 9)
- 生成随机请求头操作序列
- 验证最终请求头列表反映所有操作
- 验证没有重复且值正确
- 最少 100 次迭代

**API 响应 JSON 有效性** (Property 10)
- 生成随机 API 请求
- 验证响应是有效的 JSON
- 验证响应包含必需字段
- 最少 100 次迭代

**HTTP 状态码正确性** (Property 11)
- 生成各种错误条件
- 验证返回正确的 HTTP 状态码
- 最少 100 次迭代

**输入验证安全性** (Property 12)
- 生成随机 SQL 注入和 XSS 攻击模式
- 验证系统正确转义/清理输入
- 最少 100 次迭代

**图像可访问性** (Property 13)
- 生成随机 UI 组件
- 验证所有图像都有非空 alt 属性
- 最少 100 次迭代

### 单元测试

**认证模块**：
- 用户注册验证（示例测试）
- 登录凭证验证（示例测试）
- JWT 令牌生成和验证（示例测试）
- 会话过期处理（示例测试）

**任务管理**：
- 任务创建和验证（示例测试）
- 任务状态转换（示例测试）
- 任务配置更新（示例测试）
- 任务删除和级联删除（示例测试）

**错误处理**：
- 网络错误重试逻辑
- 选择器错误恢复建议
- Cloudflare 阻止检测

### 集成测试

**API 端点**：
- 完整的任务生命周期（创建、运行、完成）
- 用户认证流程
- WebSocket 连接和消息推送
- 错误处理和恢复

**数据库**：
- 事务一致性
- 级联删除
- 索引性能

**Scrapling 集成**：
- 不同获取器的集成
- 选择器执行
- 结果收集

**选择器测试**：
- 使用真实 URL 测试选择器
- 验证匹配元素数量
- 验证预览数据正确性

### 端到端测试

**用户工作流**：
- 用户注册和登录
- 创建和配置爬虫任务
- 执行任务并监控进度
- 查看和导出结果
- 任务历史管理

### 性能测试

- 页面加载时间 < 2 秒
- API 响应时间 < 500 毫秒
- 支持 100+ 并发用户
- 大数据集导出（>100MB）使用流式传输

### 安全测试

- SQL 注入防护（属性测试）
- XSS 防护（属性测试）
- CSRF 防护
- 速率限制
- 密码加密

### 浏览器兼容性

- Chrome/Edge (最新版本)
- Firefox (最新版本)
- Safari (最新版本)
- 移动浏览器 (iOS Safari, Chrome Mobile)

### 可访问性测试

- 键盘导航支持
- 屏幕阅读器兼容性
- 颜色对比度检查
- 焦点指示器可见性

## Deployment and Scaling Strategy

### 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet / CDN                            │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                    Nginx (Reverse Proxy)                     │
│                    - SSL/TLS Termination                     │
│                    - Load Balancing                          │
│                    - Static File Serving                     │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  FastAPI App 1   │ │  FastAPI App 2   │ │  FastAPI App N   │
│  (Gunicorn)      │ │  (Gunicorn)      │ │  (Gunicorn)      │
│  - REST API      │ │  - REST API      │ │  - REST API      │
│  - WebSocket     │ │  - WebSocket     │ │  - WebSocket     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Celery Worker 1 │ │  Celery Worker 2 │ │  Celery Worker N │
│  - Task Execution│ │  - Task Execution│ │  - Task Execution│
│  - Scrapling     │ │  - Scrapling     │ │  - Scrapling     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   PostgreSQL     │ │   Redis Cache    │ │   Message Broker │
│   (Primary DB)   │ │   (Session/Cache)│ │   (RabbitMQ)     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### Docker 部署

**Dockerfile 结构**：

```dockerfile
# 前端构建阶段
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# 后端构建阶段
FROM python:3.10-slim AS backend-builder
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 最终镜像
FROM python:3.10-slim
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 复制前端构建结果
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# 复制后端代码
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY backend/ /app/backend/

# 配置文件
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 启动脚本
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 80 443
ENTRYPOINT ["/app/docker-entrypoint.sh"]
```

### Docker Compose 配置

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - scrapling-network

  api:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/scrapling
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=amqp://rabbitmq:5672//
    depends_on:
      - postgres
      - redis
      - rabbitmq
    networks:
      - scrapling-network
    restart: unless-stopped

  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile.backend
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/scrapling
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=amqp://rabbitmq:5672//
    depends_on:
      - postgres
      - redis
      - rabbitmq
    networks:
      - scrapling-network
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=scrapling
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - scrapling-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - scrapling-network
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    environment:
      - RABBITMQ_DEFAULT_USER=user
      - RABBITMQ_DEFAULT_PASS=password
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - scrapling-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:

networks:
  scrapling-network:
    driver: bridge
```

### 扩展策略

**水平扩展**：
- 多个 FastAPI 应用实例（通过 Nginx 负载均衡）
- 多个 Celery Worker 实例（处理并发任务）
- 数据库读副本用于查询优化

**垂直扩展**：
- 增加服务器 CPU 和内存
- 优化数据库查询和索引
- 增加缓存层

**缓存策略**：
- Redis 缓存用户会话
- Redis 缓存任务状态
- Redis 缓存统计数据
- CDN 缓存静态资源

**数据库优化**：
- 连接池（pgBouncer）
- 查询优化和索引
- 分区大型表（按日期）
- 定期清理过期数据

**监控和告警**：
- Prometheus 收集指标
- Grafana 可视化仪表板
- ELK Stack 日志聚合
- 告警规则（CPU、内存、响应时间）

### 高可用性

**冗余**：
- 多个 API 实例
- 多个 Worker 实例
- 数据库主从复制
- Redis 哨兵模式

**故障转移**：
- Nginx 健康检查
- 自动重启失败的容器
- 数据库故障转移
- 任务重试机制

**备份和恢复**：
- 每日数据库备份
- 备份到外部存储（S3）
- 恢复时间目标（RTO）：1 小时
- 恢复点目标（RPO）：1 小时

### 安全部署

**网络安全**：
- HTTPS/TLS 加密
- 防火墙规则
- VPC 隔离
- DDoS 防护

**应用安全**：
- 环境变量管理（不在代码中存储密钥）
- 定期安全更新
- 依赖漏洞扫描
- 代码安全审计

**数据安全**：
- 数据库加密
- 备份加密
- 访问控制
- 审计日志

### 性能优化

**前端**：
- 代码分割和懒加载
- 资源压缩（gzip）
- 图像优化
- CDN 分发

**后端**：
- 数据库查询优化
- 缓存策略
- 异步处理
- 连接池

**基础设施**：
- 自动扩展（基于 CPU/内存）
- 负载均衡
- 地理分布式部署
- 内容分发网络（CDN）



