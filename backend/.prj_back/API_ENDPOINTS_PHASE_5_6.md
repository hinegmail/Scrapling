# Scrapling Web UI - 第 5-6 阶段 API 端点文档

## 结果管理 API

### 1. 获取结果列表

**端点：** `GET /api/v1/tasks/{task_id}/results`

**描述：** 获取指定任务的结果列表，支持分页、搜索和排序

**路径参数：**
- `task_id` (UUID, 必需) - 任务 ID

**查询参数：**
- `page` (integer, 默认: 1) - 页码，最小值 1
- `page_size` (integer, 默认: 10) - 每页项数，范围 1-100
- `search` (string, 可选) - 搜索关键词，在 data 和 source_url 中搜索
- `sort_by` (string, 默认: "extracted_at") - 排序字段
- `sort_order` (string, 默认: "desc") - 排序顺序 (asc/desc)

**请求示例：**
```bash
GET /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/results?page=1&page_size=20&search=keyword&sort_order=asc
```

**响应示例 (200 OK)：**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "data": {
        "title": "Example Title",
        "price": "$99.99"
      },
      "source_url": "https://example.com/product/1",
      "extracted_at": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

**错误响应：**
- `404 Not Found` - 任务不存在
- `500 Internal Server Error` - 服务器错误

---

### 2. 获取单个结果

**端点：** `GET /api/v1/tasks/{task_id}/results/{result_id}`

**描述：** 获取指定任务的单个结果详情

**路径参数：**
- `task_id` (UUID, 必需) - 任务 ID
- `result_id` (UUID, 必需) - 结果 ID

**请求示例：**
```bash
GET /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/results/550e8400-e29b-41d4-a716-446655440001
```

**响应示例 (200 OK)：**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "title": "Example Title",
    "price": "$99.99",
    "description": "Product description",
    "rating": 4.5
  },
  "source_url": "https://example.com/product/1",
  "extracted_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**错误响应：**
- `404 Not Found` - 任务或结果不存在
- `500 Internal Server Error` - 服务器错误

---

### 3. 导出结果

**端点：** `POST /api/v1/tasks/{task_id}/results/export`

**描述：** 导出任务结果为指定格式

**路径参数：**
- `task_id` (UUID, 必需) - 任务 ID

**查询参数：**
- `format_type` (string, 必需) - 导出格式: csv, json, excel
- `columns` (array[string], 可选) - 要导出的列名列表

**请求示例：**
```bash
POST /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/results/export?format_type=csv&columns=title&columns=price
```

**响应示例 (200 OK)：**
```
Content-Type: text/csv
Content-Disposition: attachment; filename=results.csv

id,task_id,source_url,extracted_at,created_at,title,price
550e8400-e29b-41d4-a716-446655440001,550e8400-e29b-41d4-a716-446655440000,https://example.com/product/1,2024-01-15T10:30:00Z,2024-01-15T10:30:00Z,Example Title,$99.99
```

**支持的格式：**
- `csv` - 逗号分隔值
- `json` - JSON 格式
- `excel` - Excel 工作簿

**错误响应：**
- `404 Not Found` - 任务不存在
- `422 Unprocessable Entity` - 无效的格式或无结果
- `500 Internal Server Error` - 服务器错误

---

### 4. 准备剪贴板数据

**端点：** `POST /api/v1/tasks/{task_id}/results/clipboard`

**描述：** 准备结果数据用于剪贴板，支持多种格式

**路径参数：**
- `task_id` (UUID, 必需) - 任务 ID

**查询参数：**
- `format_type` (string, 默认: "text") - 格式类型: text, json, csv, html

**请求示例：**
```bash
POST /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/results/clipboard?format_type=json
```

**响应示例 (200 OK)：**
```json
{
  "format": "json",
  "data": "[{\"id\":\"550e8400-e29b-41d4-a716-446655440001\",\"task_id\":\"550e8400-e29b-41d4-a716-446655440000\",\"source_url\":\"https://example.com/product/1\",\"extracted_at\":\"2024-01-15T10:30:00Z\",\"created_at\":\"2024-01-15T10:30:00Z\",\"data\":{\"title\":\"Example Title\",\"price\":\"$99.99\"}}]"
}
```

**支持的格式：**
- `text` - 纯文本格式
- `json` - JSON 格式
- `csv` - CSV 格式
- `html` - HTML 表格格式

**错误响应：**
- `404 Not Found` - 任务不存在
- `422 Unprocessable Entity` - 无结果
- `500 Internal Server Error` - 服务器错误

---

## 任务管理 API

### 5. 获取任务历史

**端点：** `GET /api/v1/tasks/history`

**描述：** 获取当前用户的任务历史列表

**查询参数：**
- `page` (integer, 默认: 1) - 页码
- `page_size` (integer, 默认: 10) - 每页项数，范围 1-100
- `status` (string, 可选) - 任务状态过滤: draft, running, paused, completed, failed, stopped
- `search` (string, 可选) - 按名称或描述搜索

**请求示例：**
```bash
GET /api/v1/tasks/history?page=1&page_size=20&status=completed&search=scraping
```

**响应示例 (200 OK)：**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "550e8400-e29b-41d4-a716-446655440099",
      "name": "Product Scraping Task",
      "description": "Scrape product data from example.com",
      "target_url": "https://example.com/products",
      "fetcher_type": "http",
      "selector": ".product-item",
      "selector_type": "css",
      "timeout": 30,
      "retry_count": 3,
      "status": "completed",
      "use_proxy_rotation": false,
      "solve_cloudflare": false,
      "custom_headers": null,
      "cookies": null,
      "wait_time": null,
      "viewport_width": null,
      "viewport_height": null,
      "last_run_at": "2024-01-15T10:30:00Z",
      "total_runs": 5,
      "success_count": 4,
      "error_count": 1,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2
}
```

**错误响应：**
- `500 Internal Server Error` - 服务器错误

---

### 6. 克隆任务

**端点：** `POST /api/v1/tasks/{task_id}/clone`

**描述：** 克隆现有任务，创建具有相同配置的新任务

**路径参数：**
- `task_id` (UUID, 必需) - 要克隆的任务 ID

**请求示例：**
```bash
POST /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/clone
```

**响应示例 (201 Created)：**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440099",
  "name": "Product Scraping Task (Copy)",
  "description": "Scrape product data from example.com",
  "target_url": "https://example.com/products",
  "fetcher_type": "http",
  "selector": ".product-item",
  "selector_type": "css",
  "timeout": 30,
  "retry_count": 3,
  "status": "draft",
  "use_proxy_rotation": false,
  "solve_cloudflare": false,
  "custom_headers": null,
  "cookies": null,
  "wait_time": null,
  "viewport_width": null,
  "viewport_height": null,
  "last_run_at": null,
  "total_runs": 0,
  "success_count": 0,
  "error_count": 0,
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**特点：**
- 新任务名称为 "{原名} (Copy)"
- 新任务状态为 "draft"
- 所有配置都被复制
- 统计数据重置为 0

**错误响应：**
- `404 Not Found` - 任务不存在
- `500 Internal Server Error` - 服务器错误

---

### 7. 重新运行任务

**端点：** `POST /api/v1/tasks/{task_id}/rerun`

**描述：** 使用相同配置重新运行任务

**路径参数：**
- `task_id` (UUID, 必需) - 要重新运行的任务 ID

**请求示例：**
```bash
POST /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/rerun
```

**响应示例 (201 Created)：**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440099",
  "name": "Product Scraping Task",
  "description": "Scrape product data from example.com",
  "target_url": "https://example.com/products",
  "fetcher_type": "http",
  "selector": ".product-item",
  "selector_type": "css",
  "timeout": 30,
  "retry_count": 3,
  "status": "draft",
  "use_proxy_rotation": false,
  "solve_cloudflare": false,
  "custom_headers": null,
  "cookies": null,
  "wait_time": null,
  "viewport_width": null,
  "viewport_height": null,
  "last_run_at": null,
  "total_runs": 0,
  "success_count": 0,
  "error_count": 0,
  "created_at": "2024-01-15T11:05:00Z",
  "updated_at": "2024-01-15T11:05:00Z"
}
```

**特点：**
- 创建新任务实例
- 保留原始任务名称
- 新任务状态为 "draft"
- 所有配置都被复制
- 统计数据重置为 0

**错误响应：**
- `404 Not Found` - 任务不存在
- `500 Internal Server Error` - 服务器错误

---

### 8. 删除任务

**端点：** `DELETE /api/v1/tasks/{task_id}`

**描述：** 删除任务及其所有关联的结果和日志

**路径参数：**
- `task_id` (UUID, 必需) - 要删除的任务 ID

**请求示例：**
```bash
DELETE /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000
```

**响应示例 (204 No Content)：**
```
(无响应体)
```

**特点：**
- 级联删除所有关联的结果
- 级联删除所有关联的日志
- 不可恢复操作

**错误响应：**
- `404 Not Found` - 任务不存在
- `500 Internal Server Error` - 服务器错误

---

## 认证

所有端点都需要有效的 JWT 令牌。在请求头中包含：

```
Authorization: Bearer <access_token>
```

## 错误响应格式

所有错误响应都遵循以下格式：

```json
{
  "detail": "错误描述信息"
}
```

## 速率限制

- 默认限制：100 请求/分钟
- 超过限制返回 429 Too Many Requests

## 分页

所有列表端点都支持分页：
- `page` - 页码（从 1 开始）
- `page_size` - 每页项数（1-100）
- `total` - 总项数
- `total_pages` - 总页数

## 排序

支持的排序字段：
- `extracted_at` - 提取时间（结果）
- `created_at` - 创建时间（任务）
- `updated_at` - 更新时间（任务）

排序顺序：
- `asc` - 升序
- `desc` - 降序（默认）

## 搜索

搜索功能在以下字段中进行：
- 结果：`data` 和 `source_url`
- 任务：`name` 和 `description`

搜索不区分大小写。
