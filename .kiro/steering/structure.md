# 项目结构

## 目录组织

```
Scrapling/
├── scrapling/                    # 主包
│   ├── __init__.py
│   ├── cli.py                   # 命令行界面
│   ├── core/                    # 核心功能
│   │   ├── ai.py               # MCP 服务器和 AI 集成
│   │   ├── custom_types.py     # 自定义类型定义（TextHandler 等）
│   │   ├── mixins.py           # 选择器生成混入类
│   │   ├── shell.py            # 交互式 Shell 实现
│   │   ├── storage.py          # 自适应存储系统
│   │   ├── translator.py       # XPath/CSS 转换器（来自 Parsel）
│   │   ├── _shell_signatures.py # Shell 命令签名
│   │   ├── _types.py           # 内部类型定义
│   │   ├── __init__.py
│   │   └── utils/              # 工具函数
│   │       ├── _shell.py       # Shell 工具（Cookie/Header 解析）
│   │       ├── _utils.py       # 通用工具（日志等）
│   │       └── __init__.py
│   ├── engines/                # 获取引擎
│   │   ├── constants.py        # 引擎常量
│   │   ├── static.py           # 静态 HTTP 获取器
│   │   ├── dynamic.py          # 动态浏览器获取器
│   │   ├── stealthy.py         # 隐秘模式获取器
│   │   └── toolbelt/           # 引擎工具
│   │       ├── ad_domains.py   # 广告/追踪域名列表
│   │       ├── convertor.py    # 数据转换工具
│   │       ├── custom.py       # 自定义引擎逻辑
│   │       ├── fingerprints.py # 浏览器指纹
│   │       └── __init__.py
│   ├── fetchers/               # 高级获取器 API
│   │   ├── base.py            # 基础获取器类
│   │   ├── fetcher.py         # HTTP 获取器
│   │   ├── dynamic.py         # 动态获取器
│   │   ├── stealthy.py        # 隐秘获取器
│   │   ├── sessions.py        # Session 管理
│   │   ├── proxy.py           # 代理轮换
│   │   └── __init__.py
│   ├── parser/                 # HTML/XML 解析
│   │   ├── selector.py        # 主 Selector 类
│   │   ├── element.py         # 元素包装器
│   │   ├── response.py        # 响应包装器
│   │   └── __init__.py
│   ├── spiders/                # 爬虫框架
│   │   ├── spider.py          # 基础 Spider 类
│   │   ├── request.py         # Request 类
│   │   ├── response.py        # Response 类
│   │   ├── middleware.py      # 中间件系统
│   │   ├── pipelines.py       # 结果处理管道
│   │   └── __init__.py
│   └── __init__.py            # 包导出
│
├── tests/                       # 测试套件
│   ├── requirements.txt        # 测试依赖
│   ├── test_fetchers.py       # 获取器测试
│   ├── test_parser.py         # 解析器测试
│   ├── test_spiders.py        # 爬虫测试
│   ├── test_adaptive.py       # 自适应功能测试
│   └── ...                    # 其他测试文件
│
├── docs/                        # 文档
│   ├── index.md               # 主文档
│   ├── overview.md            # 项目概览
│   ├── api-reference/         # API 文档
│   │   ├── fetchers.md
│   │   ├── spiders.md
│   │   ├── selector.md
│   │   ├── response.md
│   │   ├── custom-types.md
│   │   ├── proxy-rotation.md
│   │   └── mcp-server.md
│   ├── fetching/              # 获取指南
│   │   ├── choosing.md
│   │   ├── static.md
│   │   ├── dynamic.md
│   │   └── stealthy.md
│   ├── parsing/               # 解析指南
│   │   ├── main_classes.md
│   │   ├── selection.md
│   │   └── adaptive.md
│   ├── spiders/               # 爬虫指南
│   │   ├── architecture.md
│   │   ├── getting-started.md
│   │   ├── sessions.md
│   │   ├── requests-responses.md
│   │   ├── advanced.md
│   │   └── proxy-blocking.md
│   ├── cli/                   # CLI 文档
│   │   ├── overview.md
│   │   ├── interactive-shell.md
│   │   └── extract-commands.md
│   ├── tutorials/             # 教程
│   │   ├── migrating_from_beautifulsoup.md
│   │   └── replacing_ai.md
│   ├── development/           # 开发文档
│   │   ├── adaptive_storage_system.md
│   │   └── scrapling_custom_types.md
│   ├── ai/                    # AI 集成文档
│   │   └── mcp-server.md
│   ├── assets/                # 图片和媒体
│   ├── stylesheets/           # 文档 CSS
│   ├── overrides/             # 文档模板覆盖
│   ├── benchmarks.md          # 性能基准
│   ├── donate.md              # 捐赠信息
│   └── requirements.txt       # 文档构建依赖
│
├── agent-skill/                # AI 代理技能
│   ├── README.md
│   ├── Scrapling-Skill/
│   │   ├── SKILL.md           # 技能文档
│   │   ├── examples/          # 使用示例
│   │   ├── references/        # 参考文档
│   │   └── LICENSE.txt
│   └── Scrapling-Skill.zip
│
├── images/                      # 赞助商/合作伙伴徽标
│
├── .kiro/                       # Kiro 配置
│   └── steering/               # 指导文档
│
├── .github/                     # GitHub 配置
│   └── workflows/              # CI/CD 工作流
│
├── pyproject.toml             # 项目元数据和依赖
├── pytest.ini                 # Pytest 配置
├── ruff.toml                  # Ruff 检查配置
├── .pre-commit-config.yaml    # 预提交钩子
├── .bandit.yml                # Bandit 安全配置
├── .gitignore                 # Git 忽略规则
├── .dockerignore               # Docker 忽略规则
├── Dockerfile                 # Docker 镜像定义
├── MANIFEST.in                # 包清单
├── README.md                  # 主 README（多语言）
├── CONTRIBUTING.md            # 贡献指南
├── CODE_OF_CONDUCT.md         # 行为准则
├── LICENSE                    # BSD-3-Clause 许可证
├── ROADMAP.md                 # 项目路线图
├── benchmarks.py              # 性能基准
├── cleanup.py                 # 清理工具
└── .readthedocs.yaml          # ReadTheDocs 配置
```

## 关键模块描述

### `scrapling/core/`
核心工具和基础设施：
- **ai.py**：MCP 服务器实现，用于 AI 集成
- **custom_types.py**：增强的文本处理（TextHandler）
- **mixins.py**：CSS/XPath 选择器生成
- **shell.py**：交互式 Shell，支持 curl 解析
- **storage.py**：元素追踪的自适应存储
- **translator.py**：CSS 转 XPath 转换（改编自 Parsel）

### `scrapling/engines/`
低级获取实现：
- **static.py**：使用 curl_cffi 的 HTTP 获取
- **dynamic.py**：使用 Playwright 的浏览器自动化
- **stealthy.py**：反检测功能
- **toolbelt/**：支持工具（指纹、广告屏蔽等）

### `scrapling/fetchers/`
高级用户 API：
- **fetcher.py**：简单 HTTP 请求
- **dynamic.py**：浏览器自动化包装器
- **stealthy.py**：隐秘模式包装器
- **sessions.py**：持久连接的 Session 管理
- **proxy.py**：代理轮换策略

### `scrapling/parser/`
HTML/XML 解析和元素选择：
- **selector.py**：主 Selector 类，支持 CSS/XPath
- **element.py**：单个元素包装器
- **response.py**：HTTP 响应包装器

### `scrapling/spiders/`
类似 Scrapy 的爬虫框架：
- **spider.py**：具有异步支持的基础 Spider 类
- **request.py**：Request 对象
- **response.py**：Response 对象
- **middleware.py**：请求/响应中间件
- **pipelines.py**：结果处理管道

## 代码风格与约定

### 命名规范
- **类**：PascalCase（例如 `Fetcher`、`Spider`、`Selector`）
- **函数/方法**：snake_case（例如 `fetch_url`、`parse_html`）
- **常量**：UPPER_SNAKE_CASE（例如 `DEFAULT_TIMEOUT`）
- **私有**：前导下划线（例如 `_internal_method`）

### 类型提示
- 所有公共 API 都需要完整的类型提示
- 可空类型使用 `Optional[T]`
- 多种类型使用 `Union[T1, T2]`
- 泛型类型：`List[T]`、`Dict[K, V]` 等
- 异步函数：`async def` 并带有正确的返回类型

### 异步/等待
- 异步方法使用 `async def`
- 异步上下文管理器：`async with`
- 异步迭代：`async for`
- 所有浏览器操作都是异步的

### 文档
- 所有公共类和方法都需要文档字符串
- 文档字符串中的类型提示（Google 风格）
- 文档字符串中的示例（如有帮助）
- 主要目录中的 README 文件

## 测试结构

- **单元测试**：隔离测试单个组件
- **集成测试**：测试组件交互
- **浏览器测试**：标记为 `DynamicFetcher` 或 `StealthyFetcher`
- **异步测试**：标记为 `@pytest.mark.asyncio`
- **覆盖率目标**：92%+（目前维持）

## Git 工作流

- **主分支**：仅用于稳定版本发布
- **开发分支**：开发和功能工作
- **功能分支**：从 dev 分支创建 `feature/description`
- **修复分支**：从 dev 分支创建 `bugfix/description`
- **提交信息**：约定式提交（feat:、fix:、docs:、test:、refactor:、chore:）

## 重要文件

- **pyproject.toml**：依赖和元数据的单一信息源
- **pytest.ini**：测试配置（asyncio 模式、标记）
- **ruff.toml**：代码风格（120 字符行、Python 3.10+）
- **.pre-commit-config.yaml**：自动化代码质量检查
- **Dockerfile**：生产级容器，包含所有依赖
