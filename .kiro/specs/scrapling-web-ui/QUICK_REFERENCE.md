# Scrapling Web UI 设计快速参考

## 项目信息

- **项目名称**：Scrapling Web UI
- **项目类型**：全栈 Web 应用
- **工作流类型**：需求优先（Requirements-First）
- **规范 ID**：e5df4c79-18a9-4e4b-bb29-b45f16c8b24e

## 文件结构

```
.kiro/specs/scrapling-web-ui/
├── .config.kiro              # 规范配置
├── requirements.md           # 需求文档（20 个需求）
├── design.md                 # 详细设计文档
├── DESIGN_SUMMARY.md         # 设计总结
└── QUICK_REFERENCE.md        # 本文件
```

## 核心架构

### 分层架构
1. **客户端层**：React Web UI
2. **API 网关层**：Nginx 负载均衡
3. **应用层**：FastAPI 应用
4. **任务处理层**：Celery Worker
5. **数据层**：PostgreSQL + Redis

### 技术栈速览

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | React | 18+ |
| 前端 | TypeScript | 最新 |
| 前端 | Tailwind CSS | 最新 |
| 后端 | FastAPI | 最新 |
| 后端 | Python | 3.10+ |
| 数据库 | PostgreSQL | 15+ |
| 缓存 | Redis | 7+ |
| 任务队列 | Celery | 最新 |
| 消息代理 | RabbitMQ | 3.12+ |

## 核心功能模块

### 1. 认证与会话管理
- JWT 令牌认证
- 会话过期处理
- "记住我"功能（30 天）

### 2. 爬虫任务管理
- 任务创建和配置
- 任务执行和监控
- 任务暂停/恢复/停止
- 任务历史和重复使用

### 3. 实时通信
- WebSocket 进度更新
- 实时日志流
- 任务状态推送

### 4. 结果管理
- 表格展示（分页、排序、搜索）
- 多格式导出（CSV、JSON、Excel）
- 详细信息查看

### 5. 配置管理
- 代理配置和轮换
- 自定义请求头
- Cookie 导入

### 6. 仪表板
- 统计信息展示
- 趋势图表
- 资源监控

## API 端点速览

### 认证
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
```

### 任务
```
GET    /api/v1/tasks
POST   /api/v1/tasks
GET    /api/v1/tasks/{task_id}
PUT    /api/v1/tasks/{task_id}
DELETE /api/v1/tasks/{task_id}
POST   /api/v1/tasks/{task_id}/run
POST   /api/v1/tasks/{task_id}/pause
POST   /api/v1/tasks/{task_id}/resume
POST   /api/v1/tasks/{task_id}/stop
```

### 结果
```
GET    /api/v1/tasks/{task_id}/results
POST   /api/v1/tasks/{task_id}/results/export
GET    /api/v1/tasks/{task_id}/results/search
```

### 选择器
```
POST   /api/v1/selectors/validate
POST   /api/v1/selectors/test
POST   /api/v1/selectors/preview
```

## 数据模型

### 核心实体

| 实体 | 主要字段 | 关系 |
|------|---------|------|
| User | id, username, email, password_hash | 1:N Tasks, Sessions |
| Session | id, user_id, token, expires_at | N:1 User |
| Task | id, user_id, name, target_url, fetcher_type, selector | 1:N Results, Logs |
| Result | id, task_id, data, source_url | N:1 Task |
| TaskLog | id, task_id, level, message, timestamp | N:1 Task |
| Proxy | id, user_id, host, port, protocol | N:M Tasks |

### 索引策略
- 用户表：username, email
- 会话表：user_id, token, expires_at
- 任务表：user_id, status, created_at, (user_id, status)
- 结果表：task_id, extracted_at
- 日志表：task_id, timestamp, level

## WebSocket 事件

### 客户端 → 服务器
- `connect` - 连接
- `subscribe_task` - 订阅任务
- `unsubscribe_task` - 取消订阅

### 服务器 → 客户端
- `task_started` - 任务开始
- `task_progress` - 进度更新
- `task_log` - 日志消息
- `task_completed` - 任务完成
- `task_paused` - 任务暂停
- `task_resumed` - 任务恢复
- `task_stopped` - 任务停止

## 正确性属性（PBT）

共 13 个属性，每个最少 100 次迭代：

1. **选择器验证** - CSS/XPath 语法检查
2. **任务配置验证** - 必填字段检查
3. **WebSocket 消息完整性** - 消息格式验证
4. **表格分页** - 分页逻辑正确性
5. **数据导出格式** - 格式正确性（CSV/JSON/Excel）
6. **任务列表过滤** - 过滤逻辑正确性
7. **代理格式验证** - 代理地址格式检查
8. **代理轮换** - 轮换逻辑正确性
9. **请求头 CRUD** - CRUD 操作正确性
10. **API 响应 JSON** - JSON 格式验证
11. **HTTP 状态码** - 错误状态码正确性
12. **输入验证安全性** - SQL 注入和 XSS 防护
13. **图像可访问性** - Alt 文本检查

## 性能指标

| 指标 | 目标 |
|------|------|
| 页面加载时间 | < 2 秒 |
| API 响应时间 | < 500 毫秒 |
| 并发用户支持 | 100+ |
| 数据库查询 | 使用索引和缓存 |
| 大数据导出 | 流式传输 |

## 安全性

### 认证与授权
- JWT 令牌认证
- 会话管理
- 权限验证

### 数据保护
- HTTPS/TLS 加密
- 密码加密存储
- 敏感数据加密

### 输入验证
- SQL 注入防护
- XSS 防护
- CSRF 防护

### 其他
- 速率限制
- 审计日志
- 安全更新

## 部署

### Docker 部署
```bash
docker-compose up -d
```

### 服务组件
- Nginx（反向代理）
- FastAPI 应用（多实例）
- Celery Worker（多实例）
- PostgreSQL（数据库）
- Redis（缓存）
- RabbitMQ（消息代理）

### 扩展策略
- 水平扩展：多个应用和 Worker 实例
- 垂直扩展：增加服务器资源
- 缓存优化：Redis 缓存热数据
- 数据库优化：连接池、查询优化

## 测试策略

### 属性测试（PBT）
- 14 个属性，每个 100+ 次迭代
- 使用 fast-check 或 hypothesis

### 单元测试
- 认证模块
- 任务管理
- 错误处理

### 集成测试
- API 端点
- 数据库操作
- WebSocket 通信
- Scrapling 集成

### 端到端测试
- 完整用户工作流
- 跨浏览器兼容性

### 性能测试
- 页面加载时间
- API 响应时间
- 并发用户支持

### 安全测试
- SQL 注入防护
- XSS 防护
- 速率限制

## 关键决策

### 为什么选择 FastAPI？
- 高性能（基于 Starlette）
- 自动 API 文档（Swagger/OpenAPI）
- 内置数据验证（Pydantic）
- 异步支持
- 易于使用

### 为什么选择 React？
- 组件化开发
- 大生态系统
- 性能优化（虚拟 DOM）
- TypeScript 支持
- 广泛的社区支持

### 为什么选择 PostgreSQL？
- 可靠性和稳定性
- 复杂查询支持
- ACID 事务
- 扩展性
- 开源

### 为什么选择 Celery？
- 分布式任务处理
- 异步执行
- 任务重试机制
- 支持多个消息代理
- 成熟稳定

## 下一步

1. **需求审查** - 与用户确认设计
2. **设计反馈** - 收集利益相关者反馈
3. **任务分解** - 转换为开发任务
4. **原型开发** - 创建关键功能原型
5. **技术验证** - 验证技术栈可行性

## 相关文档

- 完整设计文档：`design.md`
- 设计总结：`DESIGN_SUMMARY.md`
- 需求文档：`requirements.md`
- 规范配置：`.config.kiro`

## 联系方式

如有问题或建议，请参考需求文档或设计文档中的详细信息。

