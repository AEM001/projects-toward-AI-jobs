# Day 7 实战指南：文档完善 + 部署准备 + 项目总结

## 🎯 今日目标
- 完善 API 文档
- 优化 Swagger 文档显示
- 编写部署文档
- 代码优化和重构
- 项目总结和回顾

**预计时间**: 2-3 小时  
**难度**: ⭐⭐ (入门)

---

## 📚 开始前的准备（20 分钟）

### 1. 阅读学习资料
- [FastAPI Metadata and Docs](https://fastapi.tiangolo.com/tutorial/metadata/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker 基础](https://docs.docker.com/get-started/)

---

## 🛠️ 实战步骤

### Step 1: 优化 Swagger 文档（40 分钟）⭐ 核心

更新 `src/main.py`，增强 API 文档：

```python
"""
FastAPI TODO API - 完整版
"""
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from typing import Optional
import math

from src.database.connection import get_db, init_db
from src.schemas.todo import *
from src.services.todo_service import TodoService
from src.utils.logger import logger
from src.utils.middleware import RequestLoggingMiddleware
from src.utils.exceptions import TodoNotFoundException, DatabaseException

# API 元数据
tags_metadata = [
    {
        "name": "Root",
        "description": "根路径和健康检查端点",
    },
    {
        "name": "Todos",
        "description": "TODO 任务管理操作。包括创建、读取、更新、删除任务。",
    },
    {
        "name": "Health",
        "description": "应用健康检查端点",
    },
]

app = FastAPI(
    title="FastAPI TODO API",
    description="""
    ## 功能特性
    
    这是一个完整的 RESTful TODO 管理 API，提供以下功能：
    
    * **CRUD 操作** - 创建、读取、更新、删除任务
    * **数据验证** - 自动验证请求数据
    * **数据持久化** - SQLite 数据库存储
    * **搜索和筛选** - 按状态、优先级搜索任务
    * **分页支持** - 大数据量分页查询
    * **统计功能** - 任务统计和报表
    * **批量操作** - 批量删除任务
    
    ## 技术栈
    
    * **FastAPI** - 现代高性能 Web 框架
    * **SQLAlchemy** - Python ORM
    * **Pydantic** - 数据验证
    * **SQLite** - 轻量级数据库
    
    ## 快速开始
    
    1. 创建任务：POST /todos
    2. 查看任务：GET /todos
    3. 更新任务：PUT /todos/{id}
    4. 删除任务：DELETE /todos/{id}
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
)

# 添加中间件...
# （保持之前的中间件配置）

# 路由端点...
# （保持之前的路由，添加更详细的文档字符串）
```

### Step 2: 创建 API 设计文档（30 分钟）

创建 `docs/api_design.md`：

```markdown
# FastAPI TODO API 设计文档

## 概述

FastAPI TODO API 是一个 RESTful 风格的任务管理 API，提供完整的 CRUD 操作。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Version**: 1.0.0
- **Content-Type**: `application/json`

## 认证

当前版本不需要认证。未来版本将支持 JWT Token 认证。

## 端点列表

### 1. 创建任务

**端点**: `POST /todos`

**请求体**:
```json
{
  "title": "任务标题",
  "description": "任务描述（可选）",
  "priority": "high"
}
```

**响应**: `201 Created`
```json
{
  "id": 1,
  "title": "任务标题",
  "description": "任务描述",
  "status": "pending",
  "priority": "high",
  "created_at": "2024-12-20T10:00:00",
  "updated_at": "2024-12-20T10:00:00"
}
```

### 2. 获取任务列表

**端点**: `GET /todos`

**查询参数**:
- `status` (可选): 按状态筛选 (pending, in_progress, done)
- `priority` (可选): 按优先级筛选 (low, medium, high)
- `search` (可选): 搜索关键词
- `sort_by` (可选): 排序字段
- `sort_order` (可选): 排序顺序 (asc, desc)
- `page` (可选): 页码，默认 1
- `page_size` (可选): 每页数量，默认 10

**响应**: `200 OK`
```json
{
  "todos": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

### 3. 获取单个任务

**端点**: `GET /todos/{id}`

**响应**: `200 OK` 或 `404 Not Found`

### 4. 更新任务

**端点**: `PUT /todos/{id}`

**请求体** (所有字段可选):
```json
{
  "title": "新标题",
  "description": "新描述",
  "status": "done",
  "priority": "low"
}
```

**响应**: `200 OK` 或 `404 Not Found`

### 5. 删除任务

**端点**: `DELETE /todos/{id}`

**响应**: `204 No Content` 或 `404 Not Found`

### 6. 获取统计信息

**端点**: `GET /todos/stats`

**响应**: `200 OK`
```json
{
  "total": 100,
  "pending": 50,
  "in_progress": 30,
  "done": 20,
  "high_priority": 25,
  "medium_priority": 50,
  "low_priority": 25
}
```

## 错误处理

### 错误响应格式

```json
{
  "detail": "错误详情",
  "message": "用户友好的错误消息"
}
```

### 常见错误码

- `400 Bad Request` - 请求格式错误
- `404 Not Found` - 资源不存在
- `422 Unprocessable Entity` - 数据验证失败
- `500 Internal Server Error` - 服务器内部错误

## 数据模型

### Todo

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | integer | 是 | 任务 ID（自动生成） |
| title | string | 是 | 任务标题（1-200 字符） |
| description | string | 否 | 任务描述（最多 1000 字符） |
| status | enum | 是 | 任务状态（pending, in_progress, done） |
| priority | enum | 是 | 优先级（low, medium, high） |
| created_at | datetime | 是 | 创建时间（自动生成） |
| updated_at | datetime | 是 | 更新时间（自动更新） |

## 最佳实践

1. **分页**: 获取大量数据时使用分页
2. **筛选**: 使用查询参数筛选数据
3. **搜索**: 使用 search 参数进行全文搜索
4. **错误处理**: 检查响应状态码和错误信息

## 示例代码

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# 创建任务
response = requests.post(
    f"{BASE_URL}/todos",
    json={
        "title": "学习 FastAPI",
        "priority": "high"
    }
)
print(response.json())

# 获取任务列表
response = requests.get(f"{BASE_URL}/todos")
print(response.json())
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// 创建任务
fetch(`${BASE_URL}/todos`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: '学习 FastAPI',
    priority: 'high'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 版本历史

### v1.0.0 (2024-12-20)
- 初始版本
- 基础 CRUD 操作
- 搜索和筛选功能
- 分页支持
- 统计功能
```

### Step 3: 创建部署文档（30 分钟）

创建 `docs/deployment.md`：

```markdown
# 部署指南

## 本地开发环境

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd week2-fastapi-todo

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件
# 根据需要修改配置
```

### 3. 启动应用

```bash
# 开发模式（自动重载）
uvicorn src.main:app --reload

# 生产模式
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Docker 部署

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 构建和运行

```bash
# 构建镜像
docker build -t fastapi-todo .

# 运行容器
docker run -d -p 8000:8000 fastapi-todo
```

## 生产环境部署

### 使用 Gunicorn + Uvicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动应用
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 云平台部署

### Heroku

```bash
# 创建 Procfile
echo "web: uvicorn src.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 部署
heroku create
git push heroku main
```

### Railway

1. 连接 GitHub 仓库
2. 选择项目
3. 自动部署

## 性能优化

1. **使用连接池**: 配置数据库连接池
2. **启用缓存**: 使用 Redis 缓存
3. **负载均衡**: 使用多个 worker
4. **CDN**: 静态资源使用 CDN

## 监控和日志

1. **日志收集**: 使用 ELK Stack
2. **性能监控**: 使用 Prometheus + Grafana
3. **错误追踪**: 使用 Sentry

## 安全建议

1. **HTTPS**: 使用 SSL/TLS 证书
2. **CORS**: 限制允许的域名
3. **速率限制**: 防止 API 滥用
4. **输入验证**: 严格验证用户输入
```

### Step 4: 代码优化和重构（30 分钟）

创建 `src/utils/__init__.py`：

```python
"""
工具模块导出
"""
from src.utils.logger import logger
from src.utils.exceptions import (
    TodoNotFoundException,
    TodoValidationException,
    DatabaseException
)

__all__ = [
    "logger",
    "TodoNotFoundException",
    "TodoValidationException",
    "DatabaseException"
]
```

更新 `requirements.txt`，添加生产环境依赖：

```txt
# FastAPI 框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# 数据库
sqlalchemy==2.0.23
aiosqlite==0.19.0

# 数据验证
pydantic==2.5.0
pydantic-settings==2.1.0

# 环境变量
python-dotenv==1.0.0

# 测试框架
pytest==7.4.3
pytest-cov==4.1.0
httpx==0.25.2

# 开发工具
black==23.12.0
flake8==6.1.0

# 生产环境
gunicorn==21.2.0
```

### Step 5: 项目总结和清单（20 分钟）

创建 `CHECKLIST.md`：

```markdown
# Week 2 项目完成清单

## 功能实现

- [x] 创建任务（POST /todos）
- [x] 获取任务列表（GET /todos）
- [x] 获取单个任务（GET /todos/{id}）
- [x] 更新任务（PUT /todos/{id}）
- [x] 删除任务（DELETE /todos/{id}）
- [x] 任务搜索功能
- [x] 任务筛选（状态、优先级）
- [x] 分页支持
- [x] 排序功能
- [x] 统计功能
- [x] 批量删除

## 技术实现

- [x] FastAPI 框架集成
- [x] Pydantic 数据验证
- [x] SQLAlchemy ORM
- [x] SQLite 数据库
- [x] 依赖注入
- [x] 异常处理
- [x] 日志系统
- [x] 中间件
- [x] CORS 配置

## 测试

- [x] API 端点测试
- [x] 数据验证测试
- [x] 错误处理测试
- [x] 测试覆盖率 > 80%
- [x] Postman 测试集合

## 文档

- [x] README.md
- [x] API 设计文档
- [x] 部署文档
- [x] 每日学习指南
- [x] Swagger 自动文档
- [x] 代码注释

## 代码质量

- [x] 遵循 PEP 8 规范
- [x] 类型注解
- [x] 错误处理
- [x] 日志记录
- [x] 代码模块化

## 交付物

- [x] 可运行的 API 服务
- [x] 完整的测试套件
- [x] Postman 测试集合
- [x] 完整的文档
- [x] Git 仓库

## 学习成果

- [x] 掌握 FastAPI 框架
- [x] 理解 RESTful API 设计
- [x] 学会使用 Pydantic
- [x] 掌握 SQLAlchemy ORM
- [x] 学会编写 API 测试
- [x] 理解依赖注入
- [x] 掌握异常处理
```

---

## ✅ 今日成果检查

### 最终验证

```bash
# 1. 运行所有测试
pytest tests/ -v --cov=src

# 2. 启动应用
uvicorn src.main:app --reload

# 3. 访问文档
open http://localhost:8000/docs

# 4. 检查代码风格
flake8 src/

# 5. 格式化代码
black src/ tests/
```

### 学习收获
- [x] 完善了项目文档
- [x] 优化了 API 文档
- [x] 学会了部署方法
- [x] 掌握了项目管理
- [x] 完成了完整项目

---

## 📝 Week 2 总结

### 你学到了什么？

1. **FastAPI 框架**
   - 路由和端点
   - 请求验证
   - 响应模型
   - 依赖注入
   - 中间件

2. **数据库操作**
   - SQLAlchemy ORM
   - 数据库连接
   - CRUD 操作
   - 查询优化

3. **API 设计**
   - RESTful 原则
   - HTTP 方法
   - 状态码
   - 错误处理

4. **测试**
   - pytest 框架
   - API 测试
   - 测试覆盖率
   - Postman

5. **工程化**
   - 项目结构
   - 日志系统
   - 异常处理
   - 文档编写

### 项目亮点

✨ **完整的 CRUD API**
✨ **自动数据验证**
✨ **SQLite 持久化**
✨ **搜索和筛选**
✨ **分页支持**
✨ **统计功能**
✨ **完整测试**
✨ **详细文档**

### 下一步学习

1. **用户认证** - JWT Token
2. **数据库迁移** - Alembic
3. **异步操作** - async/await
4. **缓存** - Redis
5. **消息队列** - Celery
6. **微服务** - Docker + Kubernetes

---

## 🎉 恭喜完成 Week 2！

你已经成功构建了一个完整的 FastAPI TODO API！

这是一个可以写进简历的项目：
- ✅ 现代化的技术栈
- ✅ 完整的功能实现
- ✅ 高质量的代码
- ✅ 完善的测试
- ✅ 详细的文档

**继续保持学习的热情，向 Week 3 进发！** 🚀
