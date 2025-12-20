# Day 1 实战指南：FastAPI 基础 + 项目初始化

## 🎯 今日目标
- 理解 FastAPI 框架核心概念
- 搭建完整的项目目录结构
- 创建第一个 FastAPI 应用
- 实现基础 API 端点
- 访问自动生成的 Swagger 文档

**预计时间**: 2-3 小时  
**难度**: ⭐⭐ (入门)

---

## 📚 开始前的准备（30 分钟）

### 1. 阅读学习资料
快速浏览以下文档（重点看示例）：
- [FastAPI 官方教程 - 第一步](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI 路径参数](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI 查询参数](https://fastapi.tiangolo.com/tutorial/query-params/)

### 2. 理解 FastAPI 核心概念

#### 什么是 FastAPI？
- 现代、快速（高性能）的 Web 框架
- 基于 Python 3.6+ 类型提示
- 自动生成 API 文档（Swagger UI）
- 自动数据验证（Pydantic）
- 支持异步编程

#### FastAPI vs Flask
| 特性 | FastAPI | Flask |
|------|---------|-------|
| 性能 | 非常快（与 Node.js 相当） | 较慢 |
| 数据验证 | 自动（Pydantic） | 手动 |
| API 文档 | 自动生成 | 需要插件 |
| 类型提示 | 必须 | 可选 |
| 异步支持 | 原生支持 | 需要额外配置 |

### 3. 理解项目结构
```
week2-fastapi-todo/
├── config/
│   └── settings.py          # 配置管理
├── src/
│   ├── main.py              # 今天的重点！
│   ├── models/              # 数据库模型（明天）
│   ├── schemas/             # Pydantic 模型（明天）
│   ├── routers/             # API 路由
│   ├── services/            # 业务逻辑
│   ├── database/            # 数据库配置
│   └── utils/               # 工具函数
├── tests/
├── .env
├── requirements.txt
└── README.md
```

---

## 🛠️ 实战步骤

### Step 1: 创建项目目录（10 分钟）

```bash
# 1. 进入项目目录
cd /Users/Mac/code/project/week2-fastapi-todo

# 2. 创建所有 __init__.py 文件
touch config/__init__.py
touch src/__init__.py
touch src/models/__init__.py
touch src/schemas/__init__.py
touch src/routers/__init__.py
touch src/services/__init__.py
touch src/database/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

# 3. 验证目录结构
tree -L 2
```

### Step 2: 配置虚拟环境和依赖（10 分钟）

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate  # macOS/Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python -c "import fastapi; print(fastapi.__version__)"
```

### Step 3: 创建第一个 FastAPI 应用（30 分钟）⭐ 核心

创建 `src/main.py` 文件：

```python
"""
FastAPI TODO API 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建 FastAPI 应用实例
app = FastAPI(
    title="TODO API",
    description="一个简单的 TODO 管理 API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 路径
    redoc_url="/redoc"  # ReDoc 路径
)

# 配置 CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 根路径 - 健康检查
@app.get("/")
async def root():
    """
    根路径 - API 健康检查
    """
    return {
        "message": "Welcome to TODO API",
        "status": "healthy",
        "version": "1.0.0"
    }


# 健康检查端点
@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "ok"}


# 临时的内存存储（后面会用数据库替代）
todos_db = []
todo_id_counter = 1


# 获取所有 TODO
@app.get("/todos")
async def get_todos():
    """
    获取所有 TODO 任务
    """
    return {"todos": todos_db, "count": len(todos_db)}


# 获取单个 TODO
@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    """
    根据 ID 获取单个 TODO 任务
    
    - **todo_id**: TODO 任务的唯一标识符
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            return todo
    return {"error": "Todo not found"}, 404


# 创建 TODO（简化版，明天会用 Pydantic）
@app.post("/todos")
async def create_todo(title: str, priority: str = "medium"):
    """
    创建新的 TODO 任务
    
    - **title**: 任务标题
    - **priority**: 优先级（low, medium, high）
    """
    global todo_id_counter
    
    new_todo = {
        "id": todo_id_counter,
        "title": title,
        "priority": priority,
        "status": "pending"
    }
    
    todos_db.append(new_todo)
    todo_id_counter += 1
    
    return new_todo


# 删除 TODO
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """
    删除指定的 TODO 任务
    
    - **todo_id**: 要删除的 TODO 任务 ID
    """
    global todos_db
    
    for i, todo in enumerate(todos_db):
        if todo["id"] == todo_id:
            deleted_todo = todos_db.pop(i)
            return {"message": "Todo deleted", "todo": deleted_todo}
    
    return {"error": "Todo not found"}, 404


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行
    """
    print("🚀 FastAPI 应用启动成功！")
    print("📖 访问 http://localhost:8000/docs 查看 API 文档")


# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时执行
    """
    print("👋 FastAPI 应用已关闭")
```

**代码讲解**：
1. **FastAPI 实例** - 创建应用，配置元数据
2. **CORS 中间件** - 允许跨域请求
3. **路由装饰器** - `@app.get()`, `@app.post()`, `@app.delete()`
4. **路径参数** - `{todo_id}` 自动解析和验证
5. **查询参数** - 函数参数自动成为查询参数
6. **异步函数** - 使用 `async def`（也可以用普通 `def`）
7. **生命周期事件** - `startup` 和 `shutdown` 事件

### Step 4: 启动应用（10 分钟）

```bash
# 启动开发服务器（自动重载）
uvicorn src.main:app --reload

# 指定端口
uvicorn src.main:app --reload --port 8000

# 指定主机（允许外部访问）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**预期输出**：
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
🚀 FastAPI 应用启动成功！
📖 访问 http://localhost:8000/docs 查看 API 文档
INFO:     Application startup complete.
```

### Step 5: 测试 API（30 分钟）⭐ 核心

#### 方法 1: 使用 Swagger UI（推荐）

1. 打开浏览器访问：`http://localhost:8000/docs`
2. 你会看到自动生成的交互式 API 文档
3. 点击任意端点，点击 "Try it out"
4. 填写参数，点击 "Execute"
5. 查看响应结果

#### 方法 2: 使用 curl

```bash
# 1. 健康检查
curl http://localhost:8000/

# 2. 创建 TODO
curl -X POST "http://localhost:8000/todos?title=学习FastAPI&priority=high"

# 3. 获取所有 TODO
curl http://localhost:8000/todos

# 4. 获取单个 TODO
curl http://localhost:8000/todos/1

# 5. 删除 TODO
curl -X DELETE http://localhost:8000/todos/1
```

#### 方法 3: 使用 Python requests

创建测试脚本 `test_manual.py`：

```python
import requests

BASE_URL = "http://localhost:8000"

# 创建 TODO
response = requests.post(
    f"{BASE_URL}/todos",
    params={"title": "学习 FastAPI", "priority": "high"}
)
print("创建 TODO:", response.json())

# 获取所有 TODO
response = requests.get(f"{BASE_URL}/todos")
print("所有 TODO:", response.json())

# 获取单个 TODO
response = requests.get(f"{BASE_URL}/todos/1")
print("单个 TODO:", response.json())

# 删除 TODO
response = requests.delete(f"{BASE_URL}/todos/1")
print("删除 TODO:", response.json())
```

运行测试：
```bash
python test_manual.py
```

### Step 6: 探索 API 文档（20 分钟）

#### Swagger UI (`/docs`)
- 交互式 API 文档
- 可以直接测试 API
- 查看请求/响应模型
- 查看参数说明

#### ReDoc (`/redoc`)
- 更美观的文档展示
- 适合阅读和分享
- 不能直接测试

#### OpenAPI Schema (`/openapi.json`)
- 原始的 OpenAPI 规范
- 可以导入到 Postman
- 可以生成客户端代码

### Step 7: 添加配置管理（20 分钟）

创建 `config/settings.py`：

```python
"""
应用配置管理
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    """
    # 应用信息
    app_name: str = "FastAPI TODO API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API 配置
    api_prefix: str = "/api/v1"
    
    # CORS 配置
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建配置实例
settings = Settings()
```

更新 `src/main.py` 使用配置：

```python
from config.settings import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    # ... 其他配置
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # ... 其他配置
)
```

创建 `.env` 文件：
```bash
cp .env.example .env
```

---

## ✅ 今日成果检查

### 文件清单
- [x] 完整的项目目录结构
- [x] `requirements.txt` - 依赖列表
- [x] `.gitignore` - Git 忽略配置
- [x] `.env.example` 和 `.env` - 环境变量
- [x] `src/main.py` - FastAPI 应用（约 120 行）
- [x] `config/settings.py` - 配置管理

### 功能验证
```bash
# 1. 启动应用
uvicorn src.main:app --reload

# 2. 访问文档
# 打开浏览器：http://localhost:8000/docs

# 3. 测试 API
curl http://localhost:8000/
curl -X POST "http://localhost:8000/todos?title=测试&priority=high"
curl http://localhost:8000/todos
```

### 学习收获
- [x] 理解 FastAPI 框架基础
- [x] 学会创建 FastAPI 应用
- [x] 掌握路由装饰器的使用
- [x] 了解路径参数和查询参数
- [x] 学会使用 Swagger UI 测试 API
- [x] 理解 CORS 配置
- [x] 学会使用 Pydantic Settings

---

## 💡 常见问题

### Q1: FastAPI 和 Flask 有什么区别？
**A**: FastAPI 更现代，性能更高，自动生成文档，自动数据验证。Flask 更简单，生态更成熟。

### Q2: 为什么要用 async def？
**A**: 支持异步编程，提高并发性能。初学者可以先用普通 `def`，效果一样。

### Q3: Swagger UI 是什么？
**A**: 自动生成的交互式 API 文档，可以直接在浏览器中测试 API。

### Q4: 如何修改端口？
**A**: `uvicorn src.main:app --reload --port 8080`

### Q5: 为什么访问不了 /docs？
**A**: 
1. 确认应用已启动
2. 检查端口是否正确
3. 确认没有防火墙阻止

---

## 📝 今日总结

在 Day 1，你完成了：
1. ✅ 搭建了 FastAPI 项目结构
2. ✅ 创建了第一个 FastAPI 应用
3. ✅ 实现了基础的 CRUD 端点
4. ✅ 学会了使用 Swagger UI
5. ✅ 配置了 CORS 和环境变量

**明天预告（Day 2）**：
- 学习 Pydantic 数据验证
- 创建请求/响应模型
- 实现完整的数据验证
- 优化 API 端点

---

## 🎯 作业（可选）

1. **添加更新端点**：实现 `PUT /todos/{id}` 更新任务
2. **添加查询参数**：支持按状态筛选 `GET /todos?status=pending`
3. **自定义响应**：返回更友好的错误信息
4. **探索文档**：阅读 FastAPI 官方教程前 5 章

---

**恭喜完成 Day 1！明天我们将学习 Pydantic 数据验证！** 🎉
