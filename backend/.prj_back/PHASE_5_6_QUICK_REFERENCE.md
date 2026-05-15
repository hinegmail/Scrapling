# 第 5-6 阶段快速参考指南

## 新增 API 端点

### 结果管理
```
GET    /api/v1/tasks/{task_id}/results
       查询参数: page, page_size, search, sort_by, sort_order
       返回: ResultListResponse

GET    /api/v1/tasks/{task_id}/results/{result_id}
       返回: ResultDetailResponse

POST   /api/v1/tasks/{task_id}/results/export
       查询参数: format_type (csv|json|excel), columns
       返回: 文件流

POST   /api/v1/tasks/{task_id}/results/clipboard
       查询参数: format_type (text|json|csv|html)
       返回: ClipboardData
```

### 任务管理
```
GET    /api/v1/tasks/history
       查询参数: page, page_size, status, search
       返回: TaskListResponse

POST   /api/v1/tasks/{task_id}/clone
       返回: TaskResponse (新任务)

POST   /api/v1/tasks/{task_id}/rerun
       返回: TaskResponse (新任务)

DELETE /api/v1/tasks/{task_id}
       返回: 204 No Content
```

## 核心服务方法

### ResultService
```python
# 获取结果列表
results, total = ResultService.get_results(
    db, user_id, task_id, 
    page=1, page_size=10,
    search=None, sort_by="extracted_at", sort_order="desc"
)

# 搜索结果
results, total = ResultService.search_results(
    db, user_id, task_id, search_term, page=1, page_size=10
)

# 过滤结果
results, total = ResultService.filter_results(
    db, user_id, task_id, 
    filters={"source_url": "...", "date_from": ..., "date_to": ...},
    page=1, page_size=10
)

# 获取导出数据
results = ResultService.get_results_for_export(
    db, user_id, task_id, filters=None
)
```

### ExportService
```python
# CSV 导出
csv_content = ExportService.export_to_csv(results, columns=None, stream=False)

# JSON 导出
json_content = ExportService.export_to_json(results, columns=None, stream=False)

# Excel 导出
excel_bytes = ExportService.export_to_excel(results, columns=None)

# 剪贴板数据
clipboard_data = ExportService.get_clipboard_data(results, format_type="text")
```

### TaskService
```python
# 克隆任务
new_task = TaskService.clone_task(db, user_id, task_id)

# 重新运行任务
new_task = TaskService.rerun_task(db, user_id, task_id)

# 删除任务
TaskService.delete_task(db, user_id, task_id)

# 获取任务列表
tasks, total = TaskService.get_tasks(
    db, user_id, page=1, page_size=10,
    status=None, search=None
)
```

## 数据模型

### Result
```python
{
    "id": "uuid",
    "task_id": "uuid",
    "data": {"key": "value", ...},
    "source_url": "https://example.com",
    "extracted_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### ClipboardData
```python
{
    "format": "text|json|csv|html",
    "data": "formatted data string"
}
```

## 属性测试

### 运行所有属性测试
```bash
pytest tests/test_result_pagination.py \
        tests/test_export_formats.py \
        tests/test_task_list_filtering.py -v
```

### 运行特定测试类
```bash
pytest tests/test_result_pagination.py::TestResultPagination -v
pytest tests/test_export_formats.py::TestExportFormats -v
pytest tests/test_task_list_filtering.py::TestTaskListFiltering -v
```

### 生成覆盖率报告
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

## 常见用例

### 导出任务结果为 CSV
```python
# 1. 获取结果
results = ResultService.get_results_for_export(db, user_id, task_id)

# 2. 导出为 CSV
csv_content = ExportService.export_to_csv(results, columns=["title", "price"])

# 3. 返回给客户端
return StreamingResponse(
    iter([csv_content]),
    media_type="text/csv",
    headers={"Content-Disposition": "attachment; filename=results.csv"}
)
```

### 克隆并重新运行任务
```python
# 1. 克隆任务
cloned_task = TaskService.clone_task(db, user_id, original_task_id)

# 2. 执行新任务
# 在任务执行服务中处理
```

### 搜索和过滤结果
```python
# 搜索特定关键词
results, total = ResultService.search_results(
    db, user_id, task_id, 
    search_term="keyword",
    page=1, page_size=20
)

# 按日期范围过滤
results, total = ResultService.filter_results(
    db, user_id, task_id,
    filters={
        "date_from": datetime(2024, 1, 1),
        "date_to": datetime(2024, 1, 31)
    },
    page=1, page_size=20
)
```

## 错误处理

### 常见异常
```python
from app.exceptions import NotFoundError, ValidationError

# 任务不存在
try:
    result = ResultService.get_result(db, user_id, task_id, result_id)
except NotFoundError:
    # 处理任务或结果不存在

# 无效的导出格式
try:
    ExportService.validate_export_format(format_type)
except ValidationError:
    # 处理无效格式

# 用户权限不足
try:
    task = TaskService.get_task(db, user_id, task_id)
except NotFoundError:
    # 用户无权访问此任务
```

## 性能优化建议

### 大数据集导出
```python
# 使用流式导出
csv_generator = ExportService.export_to_csv(results, stream=True)
return StreamingResponse(csv_generator, media_type="text/csv")
```

### 分页查询
```python
# 始终使用分页，避免一次加载所有数据
results, total = ResultService.get_results(
    db, user_id, task_id,
    page=page_num, page_size=50  # 合理的页面大小
)
```

### 列选择
```python
# 只导出需要的列
csv_content = ExportService.export_to_csv(
    results, 
    columns=["title", "price", "url"]  # 指定列
)
```

## 测试覆盖统计

| 测试文件 | 测试数 | 属性测试 | 迭代次数 |
|---------|--------|---------|---------|
| test_result_pagination.py | 9 | 5 | 500 |
| test_export_formats.py | 12 | 6 | 300 |
| test_task_list_filtering.py | 9 | 3 | 150 |
| **总计** | **30** | **14** | **950+** |

## 下一步

### 前端实现
- [ ] ResultsPage 组件
- [ ] HistoryPage 组件
- [ ] ExportDialog 组件
- [ ] SearchFilter 组件

### 后端增强
- [ ] 添加更多属性测试
- [ ] 实现单元测试
- [ ] 实现集成测试
- [ ] 性能优化

### 文档
- [ ] API 文档生成
- [ ] 用户指南
- [ ] 开发者指南
