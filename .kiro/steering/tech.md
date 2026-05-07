# 技术栈与构建系统

## 语言与运行时

- **Python**: 3.10+ (支持 3.10, 3.11, 3.12, 3.13)
- **类型系统**：完整的类型提示，使用 PyRight 和 MyPy 验证

## 核心依赖

### 必需依赖（始终安装）
- `lxml>=6.0.3` - HTML/XML 解析引擎
- `cssselect>=1.4.0` - CSS 选择器支持
- `orjson>=3.11.8` - 快速 JSON 序列化
- `tld>=0.13.2` - 顶级域名解析
- `w3lib>=2.4.1` - 网络工具库
- `typing_extensions` - 类型提示向后兼容

### 可选功能组

**获取器** (`pip install "scrapling[fetchers]"`)
- `curl_cffi>=0.15.0` - 具有 TLS 指纹识别的 HTTP 客户端
- `playwright==1.58.0` - 浏览器自动化
- `patchright==1.58.2` - Playwright 分支版本
- `browserforge>=1.2.4` - 浏览器指纹识别
- `apify-fingerprint-datapoints>=0.12.0` - 指纹数据
- `msgspec>=0.21.1` - 快速序列化
- `anyio>=4.13.0` - 异步工具库
- `protego>=0.6.0` - robots.txt 解析

**AI/MCP** (`pip install "scrapling[ai]"`)
- `mcp>=1.27.0` - 模型上下文协议
- `markdownify>=1.2.0` - HTML 转 Markdown
- 包含获取器依赖

**Shell** (`pip install "scrapling[shell]"`)
- `IPython>=8.37` - 交互式 Shell
- `markdownify>=1.2.0` - HTML 转 Markdown
- 包含获取器依赖

**全部** (`pip install "scrapling[all]"`)
- 安装所有可选依赖

## 构建与开发工具

### 构建系统
- **setuptools>=61.0** - 包构建工具
- **wheel** - 二进制分发格式

### 代码质量与检查
- **ruff** - 快速 Python 代码检查和格式化工具
  - 目标：Python 3.10+
  - 行长：120 字符
  - 检查项：E, F, W（错误、缺陷、警告）
- **mypy** - 静态类型检查器
- **pyright** - 微软的静态类型检查器
- **bandit** - 安全检查工具
- **vermin** - Python 版本兼容性检查

### 预提交钩子
- Ruff（代码检查 + 格式化）
- Bandit（安全检查）
- Vermin（版本兼容性检查）

### 测试工具
- **pytest** - 测试框架
- **pytest-asyncio** - 异步测试支持
- **pytest-xdist** - 并行测试执行
- **pytest-cov** - 覆盖率报告
- **pytest-httpbin** - HTTP 测试工具
- **tox** - 多环境测试

### 文档工具
- **Zensical** - 文档构建工具
- **ReadTheDocs** - 文档托管平台

## 常用命令

### 安装与设置
```bash
# 安装基础包
pip install scrapling

# 安装获取器（HTTP、浏览器自动化）
pip install "scrapling[fetchers]"

# 安装浏览器依赖
scrapling install

# 强制重新安装浏览器
scrapling install --force

# 安装所有功能
pip install "scrapling[all]"

# 开发环境设置
pip install -e ".[all]"
pip install -r tests/requirements.txt
pre-commit install
```

### 测试
```bash
# 并行运行所有测试
pytest tests -n auto

# 非浏览器测试并行运行，浏览器测试顺序运行
pytest tests/ -k "not (DynamicFetcher or StealthyFetcher)" -n auto
pytest tests/ -k "DynamicFetcher or StealthyFetcher"

# 运行并生成覆盖率报告
pytest --cov=scrapling tests/

# 运行特定测试文件
pytest tests/test_file.py -v
```

### 代码质量检查
```bash
# 运行 ruff 检查
ruff check scrapling/

# 使用 ruff 格式化代码
ruff format scrapling/

# 使用 pyright 进行类型检查
pyright

# 使用 mypy 进行类型检查
mypy scrapling/

# 使用 bandit 进行安全检查
bandit -r -c .bandit.yml scrapling/

# 版本兼容性检查
vermin -t=3.10- --violations --eval-annotations --no-tips scrapling/
```

### 文档
```bash
# 构建文档
zensical build --clean

# 本地预览文档
zensical serve
```

### CLI 使用
```bash
# 启动交互式 Shell
scrapling shell

# 从 URL 提取内容
scrapling extract get 'https://example.com' output.md
scrapling extract fetch 'https://example.com' output.md --css-selector '#selector'
scrapling extract stealthy-fetch 'https://example.com' output.md --solve-cloudflare
```

## Docker

预构建的 Docker 镜像：
- **DockerHub**: `pyd4vinci/scrapling`
- **GitHub 仓库**: `ghcr.io/d4vinci/scrapling:latest`

镜像包含所有功能和浏览器依赖。

## 版本管理

- **当前版本**：0.4.7（在 pyproject.toml 中静态定义以优化 Docker 层缓存）
- **发布渠道**：主分支用于稳定版本，dev 分支用于开发
- **Python 支持**：3.10+（通过 requires-python 强制）

## 配置文件

- `pyproject.toml` - 项目元数据、依赖、构建配置
- `pytest.ini` - Pytest 配置
- `ruff.toml` - Ruff 检查和格式化配置
- `.pre-commit-config.yaml` - 预提交钩子
- `.bandit.yml` - Bandit 安全检查配置
- `Dockerfile` - 容器镜像定义
