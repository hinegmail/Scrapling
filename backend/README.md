# Scrapling Web UI - Backend

FastAPI 后端应用，为 Scrapling Web UI 提供 REST API 和 WebSocket 支持。

## 快速开始

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑 .env 文件，配置数据库和其他服务
```

### 运行迁移

```bash
# 创建数据库表
alembic upgrade head
```

### 启动应用

```bash
# 开发模式
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload
```

应用将在 `http://localhost:8000` 启动。

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── models/                 # 数据库模型
│   │   ├── __init__.py
│   │   ├── base.py            # 基础模型
│   │   ├── user.py            # 用户模型
│   │   ├── session.py         # 会话模型
│   │   ├── task.py            # 任务模型
│   │   ├── result.py          # 结果模型
│   │   ├── task_log.py        # 日志模型
│   │   ├── proxy.py           # 代理模型
│   │   └── header.py          # 请求头模型
│   ├── schemas/                # Pydantic 模型
│   ├── api/                    # API 路由
│   │   └── v1/
│   ├── services/               # 业务逻辑
│   ├── core/                   # 核心功能
│   │   ├── security.py        # 安全相关
│   │   ├── exceptions.py      # 自定义异常
│   │   ├── logging.py         # 日志配置
│   │   └── middleware.py      # 中间件
│   ├── db/                     # 数据库配置
│   └── celery_app.py          # Celery 配置
├── tests/                      # 测试
├── alembic/                    # 数据库迁移
├── pyproject.toml             # 项目配置
├── pytest.ini                 # Pytest 配置
└── .env.example               # 环境变量示例
```

## API 文档

启动应用后，访问 `http://localhost:8000/docs` 查看 Swagger UI 文档。

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=app
```

## 开发

### 代码风格

使用 Black 和 Ruff 进行代码格式化和检查：

```bash
# 格式化代码
black app/

# 检查代码
ruff check app/
```

### 类型检查

```bash
# 使用 MyPy 进行类型检查
mypy app/
```

## 部署

参考 `docker-compose.yml` 和 `Dockerfile` 进行 Docker 部署。
