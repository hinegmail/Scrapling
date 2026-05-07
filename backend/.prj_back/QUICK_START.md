# Scrapling Web UI - 快速开始指南

## 项目概览

Scrapling Web UI 是一个现代化的全栈 Web 应用，为非技术用户提供图形化界面来使用 Scrapling 高性能网页爬取框架。

**当前进度**：第 3-4 阶段完成（后端任务管理和执行）

## 环境设置

### 前置要求
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose（可选）

### 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和 Redis 连接

# 运行数据库迁移
alembic upgrade head

# 启动 FastAPI 服务器
python -m uvicorn app.main:app --reload

# 在另一个终端启动 Celery Worker
celery -A app.celery_app worker --loglevel=info
```

### 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm run test
```

### Docker 部署

```bash
# 在项目根目录运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## API 端点

### 认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 获取当前用户

### 任务管理
- `POST /api/v1/tasks` - 创建任务
- `GET /api/v1/tasks` - 获取任务列表
- `GET /api/v1/tasks/{task_id}` - 获取任务详情
- `PUT /api/v1/tasks/{task_id}` - 更新任务
- `DELETE /api/v1/tasks/{task_id}` - 删除任务
- `POST /api/v1/tasks/{task_id}/clone` - 复制任务

### 任务执行
- `POST /api/v1/tasks/{task_id}/run` - 启动执行
- `POST /api/v1/tasks/{task_id}/pause` - 暂停任务
- `POST /api/v1/tasks/{task_id}/resume` - 恢复任务
- `POST /api/v1/tasks/{task_id}/stop` - 停止任务

### 选择器验证
- `POST /api/v1/selectors/validate` - 验证选择器语法
- `POST /api/v1/selectors/test` - 测试选择器

### 代理管理
- `POST /api/v1/config/proxies` - 创建代理
- `GET /api/v1/config/proxies` - 获取代理列表
- `GET /api/v1/config/proxies/{proxy_id}` - 获取代理详情
- `PUT /api/v1/config/proxies/{proxy_id}` - 更新代理
- `DELETE /api/v1/config/proxies/{proxy_id}` - 删除代理

### WebSocket
- `WS /api/v1/ws/tasks/{task_id}` - 任务进度实时更新

## 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_task_validation.py -v

# 运行属性测试
pytest tests/test_task_validation.py::TestTaskValidation -v

# 生成覆盖率报告
pytest --cov=app tests/
```

### 前端测试

```bash
cd frontend

# 运行所有测试
npm run test

# 运行特定测试文件
npm run test -- auth.test.ts

# 生成覆盖率报告
npm run test -- --coverage
```

## 项目结构

```
Scrapling/
├── backend/
│   ├── app/
│   │   ├── models/          # 数据模型
│   │   ├── routes/          # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── middleware/      # 中间件
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── tasks/           # Celery 任务
│   │   ├── main.py          # FastAPI 应用
│   │   ├── config.py        # 配置
│   │   ├── celery_app.py    # Celery 配置
│   │   └── websocket_manager.py  # WebSocket 管理
│   ├── tests/               # 测试文件
│   ├── alembic/             # 数据库迁移
│   ├── .prj_back/           # 项目文档
│   └── pyproject.toml       # 项目配置
│
├── frontend/
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # UI 组件
│   │   ├── api/             # API 客户端
│   │   ├── store/           # Redux 状态
│   │   ├── App.tsx          # 主应用
│   │   └── main.tsx         # 入口点
│   ├── tests/               # 测试文件
│   └── package.json         # 项目配置
│
├── docker-compose.yml       # Docker 编排
├── Dockerfile.backend       # 后端镜像
├── Dockerfile.frontend      # 前端镜像
└── .kiro/specs/             # 规范文档
```

## 常见命令

### 后端

```bash
# 启动开发服务器
python -m uvicorn app.main:app --reload

# 启动 Celery Worker
celery -A app.celery_app worker --loglevel=info

# 运行数据库迁移
alembic upgrade head

# 创建新迁移
alembic revision --autogenerate -m "description"

# 代码检查
ruff check app/

# 代码格式化
ruff format app/

# 类型检查
mypy app/

# 安全检查
bandit -r app/
```

### 前端

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run format

# 类型检查
npm run type-check
```

## 数据库

### 连接字符串

```
postgresql://user:password@localhost:5432/scrapling
```

### 常用查询

```sql
-- 查看所有用户
SELECT * FROM users;

-- 查看所有任务
SELECT * FROM tasks;

-- 查看任务结果
SELECT * FROM results WHERE task_id = 'task-uuid';

-- 查看任务日志
SELECT * FROM task_logs WHERE task_id = 'task-uuid' ORDER BY timestamp DESC;

-- 查看代理
SELECT * FROM proxies;
```

## 故障排除

### 数据库连接错误

```bash
# 检查 PostgreSQL 是否运行
psql -U user -d scrapling -c "SELECT 1"

# 检查 Redis 是否运行
redis-cli ping
```

### Celery Worker 不工作

```bash
# 检查 Redis 连接
redis-cli -n 1 PING

# 查看 Celery 日志
celery -A app.celery_app worker --loglevel=debug

# 清空 Celery 队列
celery -A app.celery_app purge
```

### WebSocket 连接失败

```bash
# 检查 WebSocket 端点
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost:8000/api/v1/ws/tasks/task-id
```

## 性能优化

### 后端

- 使用数据库连接池
- 启用查询缓存
- 使用 Redis 缓存会话
- 配置 Celery Worker 并发数

### 前端

- 代码分割和懒加载
- 资源压缩（gzip）
- 图像优化
- CDN 分发

## 安全建议

1. **环境变量**：不要在代码中存储敏感信息，使用 .env 文件
2. **HTTPS**：在生产环境中使用 HTTPS
3. **CORS**：配置适当的 CORS 策略
4. **速率限制**：启用速率限制防止滥用
5. **输入验证**：验证所有用户输入
6. **SQL 注入**：使用参数化查询
7. **XSS 防护**：转义用户输入

## 部署

### 生产环境检查清单

- [ ] 更新 SECRET_KEY
- [ ] 设置 DEBUG=False
- [ ] 配置 ALLOWED_HOSTS
- [ ] 设置 HTTPS/TLS 证书
- [ ] 配置数据库备份
- [ ] 设置日志聚合
- [ ] 配置监控和告警
- [ ] 运行安全扫描
- [ ] 性能测试
- [ ] 负载测试

### Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 清理资源
docker-compose down -v
```

## 文档

- [设计文档](../../.kiro/specs/scrapling-web-ui/design.md)
- [需求文档](../../.kiro/specs/scrapling-web-ui/requirements.md)
- [第 3-4 阶段总结](./PHASE_3_4_SUMMARY.md)
- [任务状态](./TASKS_STATUS.md)

## 联系和支持

- 项目主页：https://github.com/d4vinci/Scrapling
- 问题报告：https://github.com/d4vinci/Scrapling/issues
- 讨论：https://github.com/d4vinci/Scrapling/discussions

## 许可证

BSD-3-Clause License

