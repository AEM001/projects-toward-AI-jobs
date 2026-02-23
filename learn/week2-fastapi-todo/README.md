# Week 2: RESTful TODO API with FastAPI

## 📋 项目概述

**FastAPI TODO API** 是一个完整的 RESTful API 服务，让你可以通过 HTTP 请求管理待办事项。通过开发这个项目，你将学习现代 Web API 开发的核心技能：FastAPI 框架、Pydantic 数据验证、SQLite 数据库、RESTful 设计、API 文档等。

### 🎬 项目演示
```bash
# 启动 API 服务
$ uvicorn src.main:app --reload

# 访问自动生成的 API 文档
http://localhost:8000/docs

# 使用 curl 测试 API
$ curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"学习 FastAPI","priority":"high"}'

$ curl "http://localhost:8000/todos"
```

## 🎯 项目目标

### 功能目标
1. **完整的 CRUD 操作** - Create（创建）、Read（读取）、Update（更新）、Delete（删除）
2. **RESTful API 设计** - 符合 REST 规范的 URL 和 HTTP 方法
3. **数据验证** - 使用 Pydantic 自动验证请求数据
4. **SQLite 持久化** - 使用关系型数据库存储数据
5. **自动 API 文档** - Swagger UI 和 ReDoc 交互式文档
6. **错误处理** - 统一的异常处理和友好的错误响应
7. **状态管理** - 任务状态流转（pending → in_progress → done）
8. **过滤和搜索** - 按状态、优先级筛选任务

### 工程化目标
1. **现代 API 框架** - 掌握 FastAPI 高性能异步框架
2. **数据库集成** - SQLAlchemy ORM + SQLite
3. **请求验证** - Pydantic 模型自动验证
4. **API 测试** - pytest + httpx 测试 API 端点
5. **依赖注入** - FastAPI 的依赖注入系统
6. **CORS 配置** - 跨域资源共享设置
7. **环境配置** - 使用 .env 管理配置

### 学习成果
- ✅ 开发一个完整的 RESTful API 服务
- ✅ 掌握 FastAPI 框架核心特性
- ✅ 学会使用 Pydantic 进行数据验证
- ✅ 掌握 SQLAlchemy ORM 数据库操作
- ✅ 理解 RESTful API 设计原则
- ✅ 学会编写 API 测试
- ✅ 掌握自动生成 API 文档
- ✅ 学习异步编程基础

## 📁 项目结构

```
week2-fastapi-todo/
├── README.md                 # 项目说明文档
├── requirements.txt          # 项目依赖列表
├── .env.example              # 环境变量示例
├── .gitignore               # Git 忽略文件配置
├── config/                  # 配置文件目录
│   ├── __init__.py
│   └── settings.py          # 应用配置（数据库、CORS 等）
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── models/              # 数据模型（SQLAlchemy）
│   │   ├── __init__.py
│   │   └── todo.py          # Todo ORM 模型
│   ├── schemas/             # Pydantic 模式（请求/响应）
│   │   ├── __init__.py
│   │   └── todo.py          # Todo Schema 定义
│   ├── routers/             # API 路由
│   │   ├── __init__.py
│   │   └── todos.py         # Todo 相关路由
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   └── todo_service.py  # Todo 业务逻辑
│   ├── database/            # 数据库配置
│   │   ├── __init__.py
│   │   ├── connection.py    # 数据库连接
│   │   └── base.py          # Base 模型
│   └── utils/               # 工具模块
│       ├── __init__.py
│       └── exceptions.py    # 自定义异常
├── tests/                   # 测试目录
│   ├── __init__.py
│   ├── conftest.py          # pytest 配置和 fixtures
│   ├── test_todos_api.py    # API 端点测试
│   └── test_todo_service.py # 业务逻辑测试
├── docs/                    # 文档目录
│   ├── api_design.md        # API 设计文档
│   └── postman_collection.json  # Postman 测试集合
├── knowledge/               # 学习指南
│   ├── DAY1_GUIDE.md        # Day 1 实战指南
│   ├── DAY2_GUIDE.md        # Day 2 实战指南
│   ├── DAY3_GUIDE.md        # Day 3 实战指南
│   ├── DAY4_GUIDE.md        # Day 4 实战指南
│   ├── DAY5_GUIDE.md        # Day 5 实战指南
│   ├── DAY6_GUIDE.md        # Day 6 实战指南
│   └── DAY7_GUIDE.md        # Day 7 实战指南
└── todo.db                  # SQLite 数据库文件（运行时生成）
```

## 📅 7 天学习计划（每天 2-3 小时）

### Day 1: FastAPI 基础 + 项目初始化（周一）
**学习重点**: FastAPI 入门、路由、请求响应  
**今日目标**: 搭建项目骨架，创建第一个 API 端点

#### 任务清单
- [ ] 创建项目目录结构
- [ ] 配置 `requirements.txt` 和虚拟环境
- [ ] 创建 FastAPI 应用（main.py）
- [ ] 实现第一个 GET 端点（Hello World）
- [ ] 学习 FastAPI 路由和路径参数
- [ ] 访问自动生成的 Swagger 文档

**学习资料**:
- [FastAPI 官方教程](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI 第一步](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [路径参数](https://fastapi.tiangolo.com/tutorial/path-params/)

**交付物**: 可运行的 FastAPI 应用 + Swagger 文档

---

### Day 2: Pydantic 模型 + 请求验证（周二）
**学习重点**: Pydantic Schema、请求体验证、响应模型  
**今日目标**: 定义数据模型，实现数据验证

#### 任务清单
- [ ] 创建 Pydantic Schema（schemas/todo.py）
  - TodoBase, TodoCreate, TodoUpdate, TodoResponse
- [ ] 学习 Pydantic 字段验证（Field）
- [ ] 实现 POST 端点（创建 Todo）
- [ ] 实现请求体验证
- [ ] 学习响应模型（response_model）
- [ ] 测试数据验证功能

**学习资料**:
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)

**交付物**: 完整的 Pydantic 模型 + 数据验证

---

### Day 3: SQLite + SQLAlchemy ORM（周三）
**学习重点**: 数据库连接、ORM 模型、CRUD 操作  
**今日目标**: 集成数据库，实现数据持久化

#### 任务清单
- [ ] 配置 SQLAlchemy（database/connection.py）
- [ ] 创建 ORM 模型（models/todo.py）
- [ ] 创建数据库表（自动迁移）
- [ ] 实现数据库会话管理（依赖注入）
- [ ] 学习 SQLAlchemy 查询语法
- [ ] 测试数据库连接

**学习资料**:
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)

**交付物**: 数据库集成 + ORM 模型

---

### Day 4: CRUD API 实现（周四）
**学习重点**: RESTful 设计、HTTP 方法、业务逻辑  
**今日目标**: 实现完整的 CRUD API 端点

#### 任务清单
- [ ] 创建业务逻辑层（services/todo_service.py）
- [ ] 实现 CRUD 操作：
  - POST /todos - 创建任务
  - GET /todos - 获取任务列表
  - GET /todos/{id} - 获取单个任务
  - PUT /todos/{id} - 更新任务
  - DELETE /todos/{id} - 删除任务
- [ ] 实现状态码处理（200, 201, 404, 422）
- [ ] 添加查询参数（过滤、分页）

**学习资料**:
- [RESTful API 设计指南](https://restfulapi.net/)
- [HTTP 状态码](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status)
- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)

**交付物**: 完整的 CRUD API

---

### Day 5: 异常处理 + 高级功能（周五）
**学习重点**: 异常处理、依赖注入、中间件  
**今日目标**: 完善错误处理，添加高级功能

#### 任务清单
- [ ] 创建自定义异常（utils/exceptions.py）
- [ ] 实现全局异常处理器
- [ ] 添加 CORS 中间件
- [ ] 实现任务状态流转验证
- [ ] 添加任务搜索功能
- [ ] 实现按优先级、状态过滤

**学习资料**:
- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)

**交付物**: 完善的错误处理 + 高级功能

---

### Day 6: API 测试 + Postman 集合（周六）
**学习重点**: API 测试、pytest、httpx  
**今日目标**: 编写完整的 API 测试

#### 任务清单
- [ ] 配置 pytest 和 httpx
- [ ] 创建测试数据库（conftest.py）
- [ ] 编写 API 端点测试
  - 测试所有 CRUD 操作
  - 测试数据验证
  - 测试错误处理
- [ ] 创建 Postman 测试集合
- [ ] 运行测试覆盖率分析

**学习资料**:
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest 文档](https://docs.pytest.org/)
- [httpx 文档](https://www.python-httpx.org/)

**交付物**: 完整的测试套件 + Postman 集合

---

### Day 7: 文档完善 + 部署准备（周日）
**学习重点**: API 文档、环境配置、部署  
**今日目标**: 完善文档，准备部署

#### 任务清单
- [ ] 完善 API 文档（docs/api_design.md）
- [ ] 添加 API 端点描述和示例
- [ ] 配置环境变量（.env）
- [ ] 编写部署文档
- [ ] 优化 Swagger 文档显示
- [ ] 添加健康检查端点
- [ ] 提交代码到 GitHub

**学习资料**:
- [FastAPI Metadata and Docs](https://fastapi.tiangolo.com/tutorial/metadata/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

**交付物**: 完整文档 + 可部署的应用

## 📚 核心技术栈

### 后端框架
- **FastAPI** - 现代高性能 Web 框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证和设置管理

### 数据库
- **SQLAlchemy** - Python SQL 工具包和 ORM
- **SQLite** - 轻量级关系型数据库

### 测试
- **pytest** - 测试框架
- **httpx** - HTTP 客户端（用于测试）

### 工具
- **python-dotenv** - 环境变量管理
- **Postman** - API 测试工具

## 🚀 快速开始

### 环境准备
```bash
# 1. 进入项目目录
cd week2-fastapi-todo

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 创建环境变量文件
cp .env.example .env
```

### 启动应用
```bash
# 开发模式（自动重载）
uvicorn src.main:app --reload

# 指定端口
uvicorn src.main:app --reload --port 8000

# 访问 API 文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### API 使用示例

#### 1. 创建任务
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "学习 FastAPI",
    "description": "完成 FastAPI 教程",
    "priority": "high"
  }'
```

#### 2. 获取所有任务
```bash
curl "http://localhost:8000/todos"
```

#### 3. 获取单个任务
```bash
curl "http://localhost:8000/todos/1"
```

#### 4. 更新任务
```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "学习 FastAPI（已更新）",
    "status": "in_progress"
  }'
```

#### 5. 删除任务
```bash
curl -X DELETE "http://localhost:8000/todos/1"
```

#### 6. 按状态筛选
```bash
curl "http://localhost:8000/todos?status=pending"
```

### 运行测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_todos_api.py

# 查看测试覆盖率
pytest --cov=src tests/

# 详细输出
pytest -v tests/
```

## 📖 API 端点设计

### Todo 资源

| 方法 | 端点 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | `/todos` | 获取所有任务 | - | `List[TodoResponse]` |
| GET | `/todos/{id}` | 获取单个任务 | - | `TodoResponse` |
| POST | `/todos` | 创建新任务 | `TodoCreate` | `TodoResponse` |
| PUT | `/todos/{id}` | 更新任务 | `TodoUpdate` | `TodoResponse` |
| DELETE | `/todos/{id}` | 删除任务 | - | `{"message": "deleted"}` |

### 查询参数

- `status` - 按状态筛选（pending, in_progress, done）
- `priority` - 按优先级筛选（low, medium, high）
- `skip` - 分页偏移量
- `limit` - 每页数量

### 数据模型

#### TodoCreate（创建请求）
```json
{
  "title": "任务标题",
  "description": "任务描述（可选）",
  "priority": "high"
}
```

#### TodoUpdate（更新请求）
```json
{
  "title": "新标题（可选）",
  "description": "新描述（可选）",
  "status": "in_progress",
  "priority": "medium"
}
```

#### TodoResponse（响应）
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

## 💡 学习建议

### 学习方法
1. **先理解概念，再写代码** - 每天先学习 FastAPI 文档（30分钟）
2. **使用 Swagger 测试** - 利用自动生成的文档测试 API
3. **边写边测** - 写一个端点就测试一个端点
4. **阅读源码** - 学习 FastAPI 的实现方式
5. **对比 Flask** - 理解 FastAPI 的优势

### 时间分配建议（每天 2-3 小时）
- **阅读学习** (30-45 分钟) - FastAPI 文档和教程
- **编码实现** (60-90 分钟) - 实现当天的功能
- **测试调试** (30-45 分钟) - 使用 Swagger 和 Postman 测试
- **总结记录** (15 分钟) - 记录学习笔记

### 调试技巧
1. **使用 Swagger UI** - 最直观的测试方式
2. **查看日志** - FastAPI 的日志很详细
3. **使用 print 调试** - 在关键位置打印变量
4. **使用 Postman** - 保存测试用例
5. **阅读错误信息** - FastAPI 的错误提示很友好

## 📦 项目交付标准

### Week 2 最终交付物
1. **完整的 API 服务**
   - 所有 CRUD 端点实现
   - 数据验证完善
   - 错误处理完整
   - 代码结构清晰

2. **数据库集成**
   - SQLite 数据持久化
   - SQLAlchemy ORM 模型
   - 数据库迁移脚本

3. **测试覆盖**
   - API 端点测试覆盖率 > 80%
   - 所有测试通过
   - Postman 测试集合

4. **文档完善**
   - README.md（项目介绍、安装、使用）
   - API 设计文档
   - Swagger 自动文档
   - 代码注释

5. **Git 仓库**
   - 提交到 GitHub
   - 清晰的 commit 历史
   - 合理的 .gitignore

### 功能验收清单
- [ ] 可以创建任务（带验证）
- [ ] 可以获取所有任务
- [ ] 可以获取单个任务
- [ ] 可以更新任务
- [ ] 可以删除任务
- [ ] 可以按状态筛选任务
- [ ] 可以按优先级筛选任务
- [ ] 数据持久化到 SQLite
- [ ] 自动生成 Swagger 文档
- [ ] 所有测试通过
- [ ] Postman 集合可用

### 代码质量标准
- [ ] 遵循 PEP 8 代码风格
- [ ] 函数和类有类型注解
- [ ] API 端点有描述信息
- [ ] 异常处理完善
- [ ] 使用依赖注入
- [ ] 响应模型定义清晰

## 🎓 进阶扩展（Week 3+）

完成基础项目后，可以考虑以下扩展功能：

### 功能扩展
- [ ] 用户认证（JWT Token）
- [ ] 任务标签系统
- [ ] 任务分配（多用户）
- [ ] 任务评论功能
- [ ] 文件上传（任务附件）
- [ ] WebSocket 实时通知
- [ ] 任务统计和报表

### 技术扩展
- [ ] 使用 PostgreSQL 替代 SQLite
- [ ] 添加 Redis 缓存
- [ ] 实现 GraphQL API
- [ ] 添加 Celery 异步任务
- [ ] 集成 Elasticsearch 搜索
- [ ] 添加 Docker 容器化
- [ ] CI/CD 自动化部署
- [ ] 性能优化和监控

## 📝 注意事项

1. **异步编程**：FastAPI 支持异步，但初学可以先用同步
2. **数据验证**：充分利用 Pydantic 的验证功能
3. **依赖注入**：学习 FastAPI 的依赖注入系统
4. **类型注解**：使用类型注解提高代码质量
5. **API 设计**：遵循 RESTful 设计原则

## 🤝 学习资源

### 官方文档
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Uvicorn 文档](https://www.uvicorn.org/)

### 视频教程
- [FastAPI 完整教程](https://www.youtube.com/watch?v=7t2alSnE2-I)
- [Building a REST API with FastAPI](https://testdriven.io/blog/fastapi-crud/)

### 实战项目
- [FastAPI 最佳实践](https://github.com/zhanymkanov/fastapi-best-practices)
- [Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template)

---

**开始时间**: Week 2  
**预计完成**: 7 天  
**难度等级**: ⭐⭐⭐ (中级)

祝你学习愉快！🚀 让我们开始构建你的第一个 FastAPI 应用！
