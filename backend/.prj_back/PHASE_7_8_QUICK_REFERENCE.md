# 第 7-8 阶段快速参考

## API 端点速查表

### 仪表板 (Dashboard)
```
GET /api/v1/dashboard/statistics
  - 获取统计信息（总任务、月度任务、成功率、数据量）

GET /api/v1/dashboard/trends?days=7
  - 获取最近 N 天的趋势数据

GET /api/v1/dashboard/fetcher-stats
  - 获取各获取器类型的使用统计

GET /api/v1/dashboard/resources
  - 获取系统资源使用情况（CPU、内存、磁盘、网络）
```

### 健康检查 (Health)
```
GET /health
  - 系统健康检查（包含资源监控）
```

### API 密钥 (API Keys)
```
POST /api/v1/api-keys
  - 创建新 API 密钥
  - 参数: name, description?, expires_in_days?, permissions?

GET /api/v1/api-keys?page=1&page_size=10&is_active=true
  - 列出 API 密钥

GET /api/v1/api-keys/{api_key_id}
  - 获取 API 密钥详情

PUT /api/v1/api-keys/{api_key_id}
  - 更新 API 密钥

DELETE /api/v1/api-keys/{api_key_id}
  - 删除 API 密钥

POST /api/v1/api-keys/{api_key_id}/revoke
  - 撤销 API 密钥
```

### Webhook
```
POST /api/v1/webhooks
  - 创建 Webhook
  - 参数: name, url, events[], description?, secret?, max_retries?, retry_delay_seconds?

GET /api/v1/webhooks?page=1&page_size=10&is_active=true
  - 列出 Webhook

GET /api/v1/webhooks/{webhook_id}
  - 获取 Webhook 详情

PUT /api/v1/webhooks/{webhook_id}
  - 更新 Webhook

DELETE /api/v1/webhooks/{webhook_id}
  - 删除 Webhook

GET /api/v1/webhooks/{webhook_id}/deliveries?page=1&status=pending
  - 获取 Webhook 传递历史
```

### 文档
```
GET /api/v1/docs
  - Swagger UI 文档

GET /api/v1/redoc
  - ReDoc 文档

GET /api/v1/openapi.json
  - OpenAPI JSON 架构
```

## 认证方式

### JWT 令牌认证
```
Authorization: Bearer <jwt_token>
```

### API 密钥认证
```
X-API-Key: <api_key>
```

## 常见响应格式

### 成功响应
```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional message"
}
```

### 分页响应
```json
{
  "status": "success",
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total": 100,
    "pages": 10
  }
}
```

### 错误响应
```json
{
  "status": "error",
  "detail": "Error description",
  "code": "ERROR_CODE"
}
```

## Webhook 事件类型

```
task.created      - 任务创建
task.started      - 任务开始
task.progress     - 任务进度
task.completed    - 任务完成
task.failed       - 任务失败
task.stopped      - 任务停止
result.created    - 结果创建
```

## 服务类

### DashboardService
```python
# 获取统计信息
stats = DashboardService.get_statistics(db, user_id)

# 获取趋势数据
trends = DashboardService.get_trends(db, user_id, days=7)

# 获取获取器统计
fetcher_stats = DashboardService.get_fetcher_stats(db, user_id)

# 获取资源统计
resources = DashboardService.get_resource_stats(db, user_id)
```

### APIKeyService
```python
# 生成 API 密钥
key = APIKeyService.generate_api_key()

# 创建 API 密钥
api_key, plain_key = APIKeyService.create_api_key(
    db, user_id, name, description, expires_in_days, permissions
)

# 验证 API 密钥
api_key = APIKeyService.verify_api_key(db, plain_key)

# 获取 API 密钥
api_key = APIKeyService.get_api_key(db, user_id, api_key_id)

# 列出 API 密钥
api_keys, total = APIKeyService.get_api_keys(
    db, user_id, page, page_size, is_active
)

# 更新 API 密钥
api_key = APIKeyService.update_api_key(
    db, user_id, api_key_id, name, description, is_active, permissions
)

# 删除 API 密钥
APIKeyService.delete_api_key(db, user_id, api_key_id)

# 撤销 API 密钥
api_key = APIKeyService.revoke_api_key(db, user_id, api_key_id)
```

### WebhookService
```python
# 创建 Webhook
webhook = WebhookService.create_webhook(
    db, user_id, name, url, events, description, secret, max_retries, retry_delay_seconds
)

# 获取 Webhook
webhook = WebhookService.get_webhook(db, user_id, webhook_id)

# 列出 Webhook
webhooks, total = WebhookService.get_webhooks(
    db, user_id, page, page_size, is_active
)

# 更新 Webhook
webhook = WebhookService.update_webhook(
    db, user_id, webhook_id, name, url, events, description, is_active
)

# 删除 Webhook
WebhookService.delete_webhook(db, user_id, webhook_id)

# 创建传递记录
delivery = WebhookService.create_delivery(db, webhook_id, event, event_data)

# 传递 Webhook
success = await WebhookService.deliver_webhook(db, delivery_id, webhook, event_data)

# 获取传递历史
deliveries, total = WebhookService.get_deliveries(
    db, webhook_id, page, page_size, status
)

# 生成签名
signature = WebhookService.generate_signature(payload, secret)
```

## 中间件

### API Key 认证中间件
```python
from app.middleware.api_key_auth import get_api_key_user, require_api_key_permission

# 在路由中使用
@router.get("/protected")
async def protected_route(user: dict = Depends(get_api_key_user)):
    pass

# 需要特定权限
@router.post("/write-only")
async def write_only_route(user: dict = Depends(require_api_key_permission("write"))):
    pass
```

## 测试

### 运行所有测试
```bash
pytest backend/tests/ -v
```

### 运行特定测试文件
```bash
pytest backend/tests/test_api_keys.py -v
pytest backend/tests/test_webhooks.py -v
pytest backend/tests/test_dashboard.py -v
```

### 运行特定测试
```bash
pytest backend/tests/test_api_keys.py::TestAPIKeyService::test_create_api_key -v
```

### 生成覆盖率报告
```bash
pytest backend/tests/ --cov=app --cov-report=html
```

## 数据库迁移

### 创建新迁移
```bash
alembic revision --autogenerate -m "Add API Key and Webhook models"
```

### 应用迁移
```bash
alembic upgrade head
```

### 回滚迁移
```bash
alembic downgrade -1
```

## 常见问题

### Q: 如何创建 API 密钥？
A: 使用 `POST /api/v1/api-keys` 端点，返回的 `key` 字段是明文密钥，仅显示一次。

### Q: 如何使用 API 密钥认证？
A: 在请求头中添加 `X-API-Key: <your_api_key>`

### Q: Webhook 如何工作？
A: 创建 Webhook 后，当相应事件发生时，系统会向配置的 URL 发送 POST 请求。

### Q: 如何验证 Webhook 签名？
A: 使用 `X-Webhook-Signature` 头中的 HMAC-SHA256 签名验证请求。

### Q: 如何处理 Webhook 失败？
A: 系统会自动重试，重试次数和延迟可在创建 Webhook 时配置。

## 性能提示

1. **分页**：始终使用分页查询大量数据
2. **缓存**：资源统计和趋势数据可缓存
3. **索引**：所有查询都使用了适当的数据库索引
4. **异步**：Webhook 传递应该异步化以提高性能

## 安全提示

1. **API 密钥**：不要在代码中硬编码 API 密钥
2. **Webhook 签名**：始终验证 Webhook 签名
3. **HTTPS**：生产环境中始终使用 HTTPS
4. **权限**：使用最小权限原则配置 API 密钥权限
5. **过期**：为 API 密钥设置合理的过期时间
