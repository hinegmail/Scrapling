"""OpenAPI/Swagger documentation configuration"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    """
    Generate custom OpenAPI schema with enhanced documentation.
    
    Args:
        app: FastAPI application instance
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Scrapling Web UI API",
        version="0.1.0",
        description="""
        Scrapling Web UI API 提供完整的 REST API 接口用于网页爬虫任务管理、执行和结果处理。

        ## 主要功能

        - **用户认证**：JWT 令牌认证和会话管理
        - **任务管理**：创建、配置、执行和监控爬虫任务
        - **结果管理**：查看、搜索、过滤和导出爬取结果
        - **代理管理**：配置和轮换代理服务器
        - **选择器验证**：验证和测试 CSS/XPath 选择器
        - **仪表板统计**：查看系统使用统计和资源监控
        - **API 密钥管理**：为第三方集成创建和管理 API 密钥
        - **Webhook 支持**：配置事件通知 Webhook

        ## 认证

        ### JWT 令牌认证
        大多数端点需要 JWT 令牌认证。在请求头中包含：
        ```
        Authorization: Bearer <your_jwt_token>
        ```

        ### API 密钥认证
        第三方集成可以使用 API 密钥认证。在请求头中包含：
        ```
        X-API-Key: <your_api_key>
        ```

        ## 错误处理

        所有错误响应遵循统一格式：
        ```json
        {
            "status": "error",
            "detail": "错误描述",
            "code": "ERROR_CODE"
        }
        ```

        常见错误代码：
        - `UNAUTHORIZED`: 未授权或令牌无效
        - `FORBIDDEN`: 禁止访问
        - `NOT_FOUND`: 资源不存在
        - `VALIDATION_ERROR`: 输入验证失败
        - `INTERNAL_ERROR`: 服务器内部错误

        ## 分页

        支持分页的端点使用以下查询参数：
        - `page`: 页码（从 1 开始）
        - `page_size`: 每页项目数（默认 10，最大 100）

        分页响应包含：
        ```json
        {
            "status": "success",
            "data": [...],
            "pagination": {
                "page": 1,
                "page_size": 10,
                "total": 100,
                "pages": 10
            }
        }
        ```

        ## 速率限制

        API 实施速率限制以防止滥用。默认限制为每分钟 100 个请求。
        超过限制时返回 429 Too Many Requests。

        ## WebSocket

        实时功能通过 WebSocket 提供：
        - 任务执行进度更新
        - 实时日志流
        - 系统事件通知

        连接 WebSocket：
        ```
        ws://localhost:8000/ws/tasks/{task_id}?token=<jwt_token>
        ```
        """,
        routes=app.routes,
        tags=[
            {
                "name": "auth",
                "description": "用户认证和会话管理",
            },
            {
                "name": "tasks",
                "description": "爬虫任务管理",
            },
            {
                "name": "results",
                "description": "爬取结果管理",
            },
            {
                "name": "selectors",
                "description": "选择器验证和测试",
            },
            {
                "name": "proxies",
                "description": "代理和请求头管理",
            },
            {
                "name": "task-execution",
                "description": "任务执行控制",
            },
            {
                "name": "dashboard",
                "description": "仪表板统计和监控",
            },
            {
                "name": "api-keys",
                "description": "API 密钥管理",
            },
            {
                "name": "webhooks",
                "description": "Webhook 事件通知",
            },
        ],
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT 令牌认证",
        },
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API 密钥认证",
        },
    }

    # Add common response schemas
    openapi_schema["components"]["schemas"]["SuccessResponse"] = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["success"],
                "description": "响应状态",
            },
            "data": {
                "type": "object",
                "description": "响应数据",
            },
            "message": {
                "type": "string",
                "description": "可选的成功消息",
            },
        },
        "required": ["status", "data"],
    }

    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["error"],
                "description": "响应状态",
            },
            "detail": {
                "type": "string",
                "description": "错误详情",
            },
            "code": {
                "type": "string",
                "description": "错误代码",
            },
        },
        "required": ["status", "detail"],
    }

    openapi_schema["components"]["schemas"]["PaginationInfo"] = {
        "type": "object",
        "properties": {
            "page": {
                "type": "integer",
                "description": "当前页码",
            },
            "page_size": {
                "type": "integer",
                "description": "每页项目数",
            },
            "total": {
                "type": "integer",
                "description": "总项目数",
            },
            "pages": {
                "type": "integer",
                "description": "总页数",
            },
        },
        "required": ["page", "page_size", "total", "pages"],
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
