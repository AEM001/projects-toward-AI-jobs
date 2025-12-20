# Day 2 实战指南：Pydantic 模型 + 请求验证

## 🎯 今日目标
- 理解 Pydantic 数据验证机制
- 创建请求和响应模型（Schema）
- 实现自动数据验证
- 优化 API 端点的类型安全
- 学习 Pydantic Field 验证器

**预计时间**: 2-3 小时  
**难度**: ⭐⭐ (入门)

---

## 📚 开始前的准备（30 分钟）

### 1. 阅读学习资料
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)

### 2. 理解 Pydantic 核心概念

#### 什么是 Pydantic？
- Python 数据验证库
- 使用类型注解进行数据验证
- 自动转换数据类型
- 生成 JSON Schema
- FastAPI 的核心依赖

#### Schema vs Model
- **Schema（模式）**: Pydantic 模型，用于 API 请求/响应
- **Model（模型）**: SQLAlchemy 模型，用于数据库表

```
请求 → Pydantic Schema（验证） → 业务逻辑 → SQLAlchemy Model（数据库）
数据库 → SQLAlchemy Model → Pydantic Schema（序列化） → 响应
```

---

## 🛠️ 实战步骤

### Step 1: 创建基础 Schema（40 分钟）⭐ 核心

创建 `src/schemas/todo.py` 文件：

```python
"""
Todo Pydantic Schema
定义 API 请求和响应的数据模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class TodoStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoBase(BaseModel):
    """
    Todo 基础模型
    包含所有共享字段
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="任务标题",
        example="学习 FastAPI"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="任务描述",
        example="完成 FastAPI 教程的前 5 章"
    )
    priority: TodoPriority = Field(
        default=TodoPriority.MEDIUM,
        description="任务优先级"
    )


class TodoCreate(TodoBase):
    """
    创建 Todo 的请求模型
    继承 TodoBase，不包含 id 和时间戳
    """
    pass


class TodoUpdate(BaseModel):
    """
    更新 Todo 的请求模型
    所有字段都是可选的
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="任务标题"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="任务描述"
    )
    status: Optional[TodoStatus] = Field(
        None,
        description="任务状态"
    )
    priority: Optional[TodoPriority] = Field(
        None,
        description="任务优先级"
    )


class TodoResponse(TodoBase):
    """
    Todo 响应模型
    包含所有字段，包括 id 和时间戳
    """
    id: int = Field(..., description="任务 ID")
    status: TodoStatus = Field(default=TodoStatus.PENDING, description="任务状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        """Pydantic 配置"""
        from_attributes = True  # 允许从 ORM 模型创建
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "学习 FastAPI",
                "description": "完成 FastAPI 教程",
                "status": "pending",
                "priority": "high",
                "created_at": "2024-12-20T10:00:00",
                "updated_at": "2024-12-20T10:00:00"
            }
        }


class TodoListResponse(BaseModel):
    """
    Todo 列表响应模型
    """
    todos: list[TodoResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "todos": [
                    {
                        "id": 1,
                        "title": "学习 FastAPI",
                        "description": "完成教程",
                        "status": "pending",
                        "priority": "high",
                        "created_at": "2024-12-20T10:00:00",
                        "updated_at": "2024-12-20T10:00:00"
                    }
                ],
                "total": 1
            }
        }
```

**代码讲解**：
1. **继承结构** - `TodoBase` → `TodoCreate`/`TodoUpdate`/`TodoResponse`
2. **Field 验证器** - `min_length`, `max_length`, `description`, `example`
3. **Optional 字段** - 使用 `Optional[str]` 表示可选
4. **Enum 枚举** - 限制可选值
5. **Config 类** - 配置 Pydantic 行为
6. **from_attributes** - 允许从 ORM 对象创建

### Step 2: 更新 main.py 使用 Schema（40 分钟）⭐ 核心

更新 `src/main.py`：

```python
"""
FastAPI TODO API 主应用
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional

from src.schemas.todo import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoListResponse,
    TodoStatus,
    TodoPriority
)

app = FastAPI(
    title="TODO API",
    description="一个使用 Pydantic 验证的 TODO 管理 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 临时内存存储
todos_db = []
todo_id_counter = 1


@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "message": "Welcome to TODO API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(todo: TodoCreate):
    """
    创建新的 TODO 任务
    
    - **title**: 任务标题（必填，1-200 字符）
    - **description**: 任务描述（可选，最多 1000 字符）
    - **priority**: 优先级（low/medium/high，默认 medium）
    """
    global todo_id_counter
    
    # 创建新任务
    now = datetime.now()
    new_todo = {
        "id": todo_id_counter,
        "title": todo.title,
        "description": todo.description,
        "status": TodoStatus.PENDING,
        "priority": todo.priority,
        "created_at": now,
        "updated_at": now
    }
    
    todos_db.append(new_todo)
    todo_id_counter += 1
    
    return new_todo


@app.get("/todos", response_model=TodoListResponse)
async def get_todos(
    status: Optional[TodoStatus] = Query(None, description="按状态筛选"),
    priority: Optional[TodoPriority] = Query(None, description="按优先级筛选"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的最大记录数")
):
    """
    获取 TODO 列表
    
    支持按状态和优先级筛选，支持分页
    """
    # 筛选
    filtered_todos = todos_db
    
    if status:
        filtered_todos = [t for t in filtered_todos if t["status"] == status]
    
    if priority:
        filtered_todos = [t for t in filtered_todos if t["priority"] == priority]
    
    # 分页
    paginated_todos = filtered_todos[skip : skip + limit]
    
    return {
        "todos": paginated_todos,
        "total": len(filtered_todos)
    }


@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    """
    根据 ID 获取单个 TODO 任务
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            return todo
    
    raise HTTPException(
        status_code=404,
        detail=f"Todo with id {todo_id} not found"
    )


@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    """
    更新 TODO 任务
    
    只更新提供的字段，未提供的字段保持不变
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            # 只更新提供的字段
            update_data = todo_update.model_dump(exclude_unset=True)
            
            for field, value in update_data.items():
                todo[field] = value
            
            todo["updated_at"] = datetime.now()
            
            return todo
    
    raise HTTPException(
        status_code=404,
        detail=f"Todo with id {todo_id} not found"
    )


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """
    删除 TODO 任务
    """
    global todos_db
    
    for i, todo in enumerate(todos_db):
        if todo["id"] == todo_id:
            deleted_todo = todos_db.pop(i)
            return {
                "message": "Todo deleted successfully",
                "deleted_todo": deleted_todo
            }
    
    raise HTTPException(
        status_code=404,
        detail=f"Todo with id {todo_id} not found"
    )


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("🚀 FastAPI 应用启动成功！")
    print("📖 访问 http://localhost:8000/docs 查看 API 文档")
```

**代码讲解**：
1. **response_model** - 指定响应模型，自动序列化和验证
2. **status_code** - 指定 HTTP 状态码
3. **HTTPException** - 抛出 HTTP 异常
4. **Query 参数** - 使用 `Query()` 添加验证和描述
5. **model_dump()** - Pydantic v2 的方法，替代 v1 的 `dict()`
6. **exclude_unset** - 只包含用户设置的字段

### Step 3: 测试数据验证（30 分钟）

启动应用：
```bash
uvicorn src.main:app --reload
```

#### 测试 1: 有效数据
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "学习 FastAPI",
    "description": "完成教程",
    "priority": "high"
  }'
```

#### 测试 2: 标题太短（应该失败）
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "",
    "priority": "high"
  }'
```

预期响应：
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

#### 测试 3: 无效的优先级（应该失败）
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试",
    "priority": "urgent"
  }'
```

#### 测试 4: 更新任务
```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

#### 测试 5: 查询参数
```bash
# 按状态筛选
curl "http://localhost:8000/todos?status=pending"

# 按优先级筛选
curl "http://localhost:8000/todos?priority=high"

# 分页
curl "http://localhost:8000/todos?skip=0&limit=10"
```

### Step 4: 在 Swagger UI 中测试（20 分钟）

1. 访问 `http://localhost:8000/docs`
2. 查看自动生成的请求/响应示例
3. 测试每个端点
4. 观察验证错误的详细信息
5. 查看 Schema 定义

---

## ✅ 今日成果检查

### 文件清单
- [x] `src/schemas/__init__.py`
- [x] `src/schemas/todo.py` - Pydantic Schema（约 150 行）
- [x] 更新的 `src/main.py` - 使用 Schema 的 API（约 180 行）

### 功能验证
```bash
# 1. 启动应用
uvicorn src.main:app --reload

# 2. 测试创建（有效数据）
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试","priority":"high"}'

# 3. 测试验证（无效数据）
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"","priority":"invalid"}'

# 4. 测试更新
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"status":"done"}'
```

### 学习收获
- [x] 理解 Pydantic 数据验证机制
- [x] 学会创建请求/响应模型
- [x] 掌握 Field 验证器的使用
- [x] 理解 response_model 的作用
- [x] 学会使用 Query 参数验证
- [x] 掌握 HTTPException 异常处理

---

## 💡 常见问题

### Q1: Schema 和 Model 有什么区别？
**A**: Schema（Pydantic）用于 API 验证，Model（SQLAlchemy）用于数据库。

### Q2: 为什么要分 TodoCreate、TodoUpdate、TodoResponse？
**A**: 
- **TodoCreate**: 创建时不需要 id 和时间戳
- **TodoUpdate**: 更新时所有字段可选
- **TodoResponse**: 响应包含所有字段

### Q3: Field(...) 中的 ... 是什么意思？
**A**: 表示必填字段，等同于 `required=True`。

### Q4: model_dump() 和 dict() 有什么区别？
**A**: Pydantic v2 使用 `model_dump()`，v1 使用 `dict()`。

### Q5: 如何自定义验证逻辑？
**A**: 使用 `@field_validator` 装饰器或 `@model_validator`。

---

## 📝 今日总结

在 Day 2，你完成了：
1. ✅ 创建了完整的 Pydantic Schema
2. ✅ 实现了自动数据验证
3. ✅ 学会了使用 Field 验证器
4. ✅ 掌握了 response_model
5. ✅ 实现了查询参数验证

**明天预告（Day 3）**：
- 集成 SQLite 数据库
- 学习 SQLAlchemy ORM
- 实现数据持久化
- 创建数据库模型

---

## 🎯 作业（可选）

1. **添加自定义验证**: 使用 `@field_validator` 验证标题不能包含特殊字符
2. **添加更多字段**: 为 Todo 添加 `due_date`（截止日期）字段
3. **优化响应**: 创建统一的响应格式（包含 success、data、message）
4. **探索 Pydantic**: 阅读 Pydantic 文档，了解更多验证器

---

**恭喜完成 Day 2！明天我们将集成数据库！** 🎉
