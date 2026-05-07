# Scrapling Web UI 设计总结

## 设计概览

本设计文档为 Scrapling Web UI 项目提供了完整的系统架构、技术栈选择、数据模型设计和测试策略。

## 关键设计决策

### 1. 技术栈选择

**前端**：
- React 18+ with TypeScript：提供类型安全和现代开发体验
- Redux Toolkit / Zustand：灵活的状态管理
- Tailwind CSS + shadcn/ui：快速构建美观的 UI
- Socket.io-client：实时 WebSocket 通信

**后端**：
- FastAPI：高性能、易于使用的现代 Python Web 框架
- SQLAlchemy + Pydantic：强大的 ORM 和数据验证
- Celery：分布式任务队列，支持异步爬虫执行
- python-socketio：WebSocket 实时通信

**数据库**：
- PostgreSQL：可靠的关系型数据库，支持复杂查询
- Redis：高性能缓存和会话存储

### 2. 架构设计

采用**分层架构**：
- **客户端层**：React Web UI，提供用户界面
- **API 网关层**：Nginx 负载均衡和反向代理
- **应用层**：FastAPI 应用处理 REST API 和 WebSocket
- **任务处理层**：Celery Worker 执行爬虫任务
- **数据层**：PostgreSQL 和 Redis

这种设计支持：
- 水平扩展（多个应用实例和 Worker）
- 高可用性（冗余和故障转移）
- 性能优化（缓存和异步处理）

### 3. 实时通信设计

使用 **WebSocket** 实现实时进度更新：
- 客户端订阅特定任务的进度更新
- 服务器推送进度、日志和状态变化
- 支持多个并发连接

WebSocket 消息格式包含：
- 任务 ID、处理数量、成功率、当前 URL
- 日志级别、消息内容、时间戳
- 任务完成状态、总耗时、统计信息

### 4. 数据模型设计

核心实体：
- **User**：用户账户和认证信息
- **Session**：用户会话和 JWT 令牌
- **Task**：爬虫任务配置和状态
- **Result**：提取的数据结果
- **TaskLog**：任务执行日志
- **Proxy**：代理配置

关键设计特点：
- 完整的索引策略优化查询性能
- 级联删除确保数据一致性
- JSON 字段存储灵活的配置数据

### 5. 正确性属性（Property-Based Testing）

识别了 14 个适合属性测试的功能：

1. **选择器验证**：CSS/XPath 语法验证
2. **任务配置验证**：必填字段检查
3. **WebSocket 消息完整性**：消息格式验证
4. **表格分页**：分页逻辑正确性
5. **数据导出格式**：CSV/JSON/Excel 格式正确性
6. **任务列表过滤**：过滤逻辑正确性
7. **代理格式验证**：代理地址格式验证
8. **代理轮换**：轮换逻辑正确性
9. **请求头 CRUD**：CRUD 操作正确性
10. **API 响应 JSON 有效性**：JSON 格式验证
11. **HTTP 状态码正确性**：错误状态码正确性
12. **输入验证安全性**：SQL 注入和 XSS 防护
13. **图像可访问性**：Alt 文本检查
14. **表单字段可访问性**：标签和错误消息检查

每个属性都配置为最少 100 次迭代的属性测试。

### 6. 错误处理策略

分类错误类型：
- **认证错误** (401)：无效凭证、令牌过期
- **验证错误** (400)：无效输入、缺少必填字段
- **资源错误** (404)：资源不存在
- **业务逻辑错误** (422)：状态冲突、无效操作
- **服务器错误** (500)：数据库错误、未预期异常

提供恢复建议：
- 网络错误：自动重试
- 选择器错误：建议修改选择器
- Cloudflare 阻止：建议使用隐秘获取器
- 超时：建议增加超时时间

### 7. 部署和扩展

**Docker 部署**：
- 多阶段构建优化镜像大小
- Docker Compose 编排多个服务
- 支持快速部署和扩展

**扩展策略**：
- 水平扩展：多个应用实例和 Worker
- 垂直扩展：增加服务器资源
- 缓存优化：Redis 缓存热数据
- 数据库优化：连接池、查询优化、分区

**高可用性**：
- 多实例冗余
- 数据库主从复制
- 自动故障转移
- 定期备份和恢复

## API 端点设计

### 认证相关
- POST /api/v1/auth/register - 注册
- POST /api/v1/auth/login - 登录
- POST /api/v1/auth/logout - 登出
- POST /api/v1/auth/refresh - 刷新令牌

### 任务管理
- GET /api/v1/tasks - 获取任务列表
- POST /api/v1/tasks - 创建任务
- GET /api/v1/tasks/{task_id} - 获取任务详情
- PUT /api/v1/tasks/{task_id} - 更新任务
- DELETE /api/v1/tasks/{task_id} - 删除任务
- POST /api/v1/tasks/{task_id}/run - 执行任务
- POST /api/v1/tasks/{task_id}/pause - 暂停任务
- POST /api/v1/tasks/{task_id}/resume - 恢复任务
- POST /api/v1/tasks/{task_id}/stop - 停止任务

### 结果管理
- GET /api/v1/tasks/{task_id}/results - 获取结果
- POST /api/v1/tasks/{task_id}/results/export - 导出结果
- GET /api/v1/tasks/{task_id}/results/search - 搜索结果

### 选择器验证
- POST /api/v1/selectors/validate - 验证选择器
- POST /api/v1/selectors/test - 测试选择器
- POST /api/v1/selectors/preview - 获取预览

### 配置管理
- GET/POST /api/v1/config/proxies - 代理管理
- GET/POST /api/v1/config/headers - 请求头管理
- POST /api/v1/config/cookies/import - 导入 Cookie

### 仪表板
- GET /api/v1/dashboard/statistics - 统计信息
- GET /api/v1/dashboard/trends - 趋势数据
- GET /api/v1/dashboard/resources - 资源使用

## WebSocket 事件

### 客户端发送
- connect - 连接
- disconnect - 断开
- subscribe_task - 订阅任务
- unsubscribe_task - 取消订阅

### 服务器推送
- task_started - 任务开始
- task_progress - 进度更新
- task_log - 日志消息
- task_completed - 任务完成
- task_paused - 任务暂停
- task_resumed - 任务恢复
- task_stopped - 任务停止

## 测试策略

### 属性测试（14 个）
- 最少 100 次迭代
- 覆盖验证、格式、逻辑、安全性
- 使用 fast-check 或 hypothesis

### 单元测试
- 认证模块
- 任务管理
- 错误处理

### 集成测试
- API 端点
- 数据库操作
- Scrapling 集成
- WebSocket 通信

### 端到端测试
- 完整用户工作流
- 跨浏览器兼容性

### 性能测试
- 页面加载 < 2 秒
- API 响应 < 500 毫秒
- 支持 100+ 并发用户

### 安全测试
- SQL 注入防护
- XSS 防护
- CSRF 防护
- 速率限制

## 关键指标

### 性能
- 页面加载时间：< 2 秒
- API 响应时间：< 500 毫秒
- 并发用户支持：100+
- 数据库查询优化：使用索引和缓存

### 可靠性
- 任务暂停/恢复：支持检查点
- 错误恢复：自动重试和建议
- 数据持久化：所有数据保存到数据库
- 备份策略：每日自动备份

### 安全性
- 认证：JWT 令牌
- 加密：HTTPS/TLS
- 输入验证：防止 SQL 注入和 XSS
- 速率限制：防止暴力攻击

### 可用性
- 响应式设计：桌面、平板、移动
- 主题支持：浅色、深色
- 可访问性：键盘导航、屏幕阅读器

## 下一步

1. **需求审查**：与用户确认设计是否满足所有需求
2. **设计反馈**：收集利益相关者的反馈
3. **任务分解**：将设计转换为具体的开发任务
4. **原型开发**：创建关键功能的原型
5. **技术验证**：验证技术栈的可行性

## 文档引用

- 需求文档：`.kiro/specs/scrapling-web-ui/requirements.md`
- 设计文档：`.kiro/specs/scrapling-web-ui/design.md`
- 配置文件：`.kiro/specs/scrapling-web-ui/.config.kiro`

