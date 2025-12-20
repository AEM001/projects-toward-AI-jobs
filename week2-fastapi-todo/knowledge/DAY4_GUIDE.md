# Day 4 实战指南：完善 CRUD API + 高级功能

## 🎯 今日目标
- 完善所有 CRUD 操作
- 实现高级查询功能（搜索、排序）
- 添加批量操作
- 优化 API 响应格式
- 实现任务统计功能

**预计时间**: 2-3 小时  
**难度**: ⭐⭐⭐ (中级)

---

## 📚 开始前的准备（30 分钟）

### 1. 阅读学习资料
- [RESTful API 设计最佳实践](https://restfulapi.net/)
- [SQLAlchemy 高级查询](https://docs.sqlalchemy.org/en/20/orm/queryguide/)
- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)

### 2. 理解 RESTful API 设计原则

#### HTTP 方法语义
| 方法 | 用途 | 幂等性 | 安全性 |
|------|------|--------|--------|
| GET | 获取资源 | ✅ | ✅ |
| POST | 创建资源 | ❌ | ❌ |
| PUT | 完整更新 | ✅ | ❌ |
| PATCH | 部分更新 | ❌ | ❌ |
| DELETE | 删除资源 | ✅ | ❌ |

#### HTTP 状态码
- **200 OK** - 成功
- **201 Created** - 创建成功
- **204 No Content** - 删除成功（无返回内容）
- **400 Bad Request** - 请求错误
- **404 Not Found** - 资源不存在
- **422 Unprocessable Entity** - 验证失败

---

## 🛠️ 实战步骤

### Step 1: 扩展 Schema（30 分钟）

更新 `src/schemas/todo.py`，添加更多功能：

```python
"""
扩展的 Todo Schema
"""
from datetime import datetime
from typing import Optional, List
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


class SortOrder(str, Enum):
    """排序顺序"""
    ASC = "asc"
    DESC = "desc"


class TodoSortField(str, Enum):
    """可排序字段"""
    ID = "id"
    TITLE = "title"
    PRIORITY = "priority"
    STATUS = "status"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TodoBase(BaseModel):
    """Todo 基础模型"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="任务标题"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="任务描述"
    )
    priority: TodoPriority = Field(
        default=TodoPriority.MEDIUM,
        description="任务优先级"
    )


class TodoCreate(TodoBase):
    """创建 Todo 的请求模型"""
    pass


class TodoUpdate(BaseModel):
    """更新 Todo 的请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None


class TodoResponse(TodoBase):
    """Todo 响应模型"""
    id: int
    status: TodoStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TodoListResponse(BaseModel):
    """Todo 列表响应模型"""
    todos: List[TodoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TodoStatsResponse(BaseModel):
    """Todo 统计响应模型"""
    total: int
    pending: int
    in_progress: int
    done: int
    high_priority: int
    medium_priority: int
    low_priority: int


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., min_items=1, description="要删除的 ID 列表")


class BatchDeleteResponse(BaseModel):
    """批量删除响应"""
    deleted_count: int
    failed_ids: List[int] = []
```

### Step 2: 扩展服务层（40 分钟）⭐ 核心

更新 `src/services/todo_service.py`：

```python
"""
扩展的 Todo 服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional, Tuple

from src.models.todo import Todo, TodoStatus, TodoPriority
from src.schemas.todo import TodoCreate, TodoUpdate, TodoSortField, SortOrder


class TodoService:
    """Todo 服务类"""
    
    @staticmethod
    def create_todo(db: Session, todo: TodoCreate) -> Todo:
        """创建新的 Todo"""
        db_todo = Todo(
            title=todo.title,
            description=todo.description,
            priority=todo.priority,
            status=TodoStatus.PENDING
        )
        
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        
        return db_todo
    
    @staticmethod
    def get_todo(db: Session, todo_id: int) -> Optional[Todo]:
        """根据 ID 获取 Todo"""
        return db.query(Todo).filter(Todo.id == todo_id).first()
    
    @staticmethod
    def get_todos(
        db: Session,
        status: Optional[TodoStatus] = None,
        priority: Optional[TodoPriority] = None,
        search: Optional[str] = None,
        sort_by: TodoSortField = TodoSortField.CREATED_AT,
        sort_order: SortOrder = SortOrder.DESC,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Todo], int]:
        """
        获取 Todo 列表（带搜索、排序、分页）
        
        Returns:
            (todos, total_count)
        """
        query = db.query(Todo)
        
        # 筛选
        if status:
            query = query.filter(Todo.status == status)
        if priority:
            query = query.filter(Todo.priority == priority)
        
        # 搜索（标题或描述）
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Todo.title.ilike(search_pattern),
                    Todo.description.ilike(search_pattern)
                )
            )
        
        # 获取总数
        total = query.count()
        
        # 排序
        sort_column = getattr(Todo, sort_by.value)
        if sort_order == SortOrder.DESC:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # 分页
        todos = query.offset(skip).limit(limit).all()
        
        return todos, total
    
    @staticmethod
    def update_todo(
        db: Session,
        todo_id: int,
        todo_update: TodoUpdate
    ) -> Optional[Todo]:
        """更新 Todo"""
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        
        if not db_todo:
            return None
        
        update_data = todo_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_todo, field, value)
        
        db.commit()
        db.refresh(db_todo)
        
        return db_todo
    
    @staticmethod
    def delete_todo(db: Session, todo_id: int) -> bool:
        """删除 Todo"""
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        
        if not db_todo:
            return False
        
        db.delete(db_todo)
        db.commit()
        
        return True
    
    @staticmethod
    def batch_delete_todos(db: Session, todo_ids: List[int]) -> Tuple[int, List[int]]:
        """
        批量删除 Todo
        
        Returns:
            (deleted_count, failed_ids)
        """
        deleted_count = 0
        failed_ids = []
        
        for todo_id in todo_ids:
            db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
            if db_todo:
                db.delete(db_todo)
                deleted_count += 1
            else:
                failed_ids.append(todo_id)
        
        db.commit()
        
        return deleted_count, failed_ids
    
    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        获取 Todo 统计信息
        
        Returns:
            统计数据字典
        """
        total = db.query(Todo).count()
        
        # 按状态统计
        pending = db.query(Todo).filter(Todo.status == TodoStatus.PENDING).count()
        in_progress = db.query(Todo).filter(Todo.status == TodoStatus.IN_PROGRESS).count()
        done = db.query(Todo).filter(Todo.status == TodoStatus.DONE).count()
        
        # 按优先级统计
        high_priority = db.query(Todo).filter(Todo.priority == TodoPriority.HIGH).count()
        medium_priority = db.query(Todo).filter(Todo.priority == TodoPriority.MEDIUM).count()
        low_priority = db.query(Todo).filter(Todo.priority == TodoPriority.LOW).count()
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "done": done,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority
        }
    
    @staticmethod
    def delete_completed_todos(db: Session) -> int:
        """
        删除所有已完成的 Todo
        
        Returns:
            删除的数量
        """
        deleted = db.query(Todo).filter(Todo.status == TodoStatus.DONE).delete()
        db.commit()
        
        return deleted
```

### Step 3: 更新路由（40 分钟）⭐ 核心

更新 `src/main.py`：

```python
"""
完整的 FastAPI TODO API
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import math

from src.database.connection import get_db, init_db
from src.schemas.todo import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoListResponse,
    TodoStatsResponse,
    TodoStatus,
    TodoPriority,
    TodoSortField,
    SortOrder,
    BatchDeleteRequest,
    BatchDeleteResponse
)
from src.services.todo_service import TodoService

app = FastAPI(
    title="TODO API",
    description="完整的 RESTful TODO 管理 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    init_db()
    print("🚀 FastAPI 应用启动成功！")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to TODO API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/todos", response_model=TodoResponse, status_code=201, tags=["Todos"])
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
):
    """创建新的 TODO 任务"""
    return TodoService.create_todo(db, todo)


@app.get("/todos", response_model=TodoListResponse, tags=["Todos"])
async def get_todos(
    status: Optional[TodoStatus] = Query(None, description="按状态筛选"),
    priority: Optional[TodoPriority] = Query(None, description="按优先级筛选"),
    search: Optional[str] = Query(None, description="搜索标题或描述"),
    sort_by: TodoSortField = Query(TodoSortField.CREATED_AT, description="排序字段"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="排序顺序"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取 TODO 列表
    
    支持筛选、搜索、排序和分页
    """
    skip = (page - 1) * page_size
    
    todos, total = TodoService.get_todos(
        db=db,
        status=status,
        priority=priority,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=page_size
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return {
        "todos": todos,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@app.get("/todos/stats", response_model=TodoStatsResponse, tags=["Todos"])
async def get_stats(db: Session = Depends(get_db)):
    """获取 TODO 统计信息"""
    return TodoService.get_stats(db)


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """获取单个 TODO 任务"""
    todo = TodoService.get_todo(db, todo_id)
    
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db)
):
    """更新 TODO 任务"""
    todo = TodoService.update_todo(db, todo_id, todo_update)
    
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return todo


@app.delete("/todos/{todo_id}", status_code=204, tags=["Todos"])
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """删除 TODO 任务"""
    success = TodoService.delete_todo(db, todo_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return None


@app.post("/todos/batch-delete", response_model=BatchDeleteResponse, tags=["Todos"])
async def batch_delete_todos(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db)
):
    """批量删除 TODO 任务"""
    deleted_count, failed_ids = TodoService.batch_delete_todos(db, request.ids)
    
    return {
        "deleted_count": deleted_count,
        "failed_ids": failed_ids
    }


@app.delete("/todos/completed/all", tags=["Todos"])
async def delete_completed_todos(db: Session = Depends(get_db)):
    """删除所有已完成的 TODO 任务"""
    deleted_count = TodoService.delete_completed_todos(db)
    
    return {
        "message": f"Deleted {deleted_count} completed todos",
        "deleted_count": deleted_count
    }
```

### Step 4: 测试高级功能（30 分钟）

```bash
# 1. 创建测试数据
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"学习 Python","priority":"high"}'

curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"学习 FastAPI","priority":"medium"}'

# 2. 测试搜索
curl "http://localhost:8000/todos?search=Python"

# 3. 测试排序
curl "http://localhost:8000/todos?sort_by=priority&sort_order=desc"

# 4. 测试分页
curl "http://localhost:8000/todos?page=1&page_size=5"

# 5. 测试统计
curl "http://localhost:8000/todos/stats"

# 6. 测试批量删除
curl -X POST "http://localhost:8000/todos/batch-delete" \
  -H "Content-Type: application/json" \
  -d '{"ids":[1,2,3]}'

# 7. 删除已完成任务
curl -X DELETE "http://localhost:8000/todos/completed/all"
```

---

## ✅ 今日成果检查

### 功能验证
- [x] 搜索功能正常
- [x] 排序功能正常
- [x] 分页功能正常
- [x] 统计功能正常
- [x] 批量删除功能正常
- [x] Swagger 文档完整

### 学习收获
- [x] 掌握高级查询（搜索、排序）
- [x] 学会实现分页
- [x] 理解批量操作
- [x] 掌握统计查询
- [x] 学会使用 tags 组织 API

---

## 💡 常见问题

### Q1: 为什么要分页？
**A**: 避免一次返回太多数据，提高性能和用户体验。

### Q2: ilike 和 like 有什么区别？
**A**: `ilike` 是不区分大小写的模糊查询，`like` 区分大小写。

### Q3: 如何优化搜索性能？
**A**: 为搜索字段添加索引，使用全文搜索引擎（如 Elasticsearch）。

---

## 📝 今日总结

在 Day 4，你完成了：
1. ✅ 实现了搜索功能
2. ✅ 实现了排序功能
3. ✅ 实现了分页功能
4. ✅ 实现了统计功能
5. ✅ 实现了批量操作

**明天预告（Day 5）**：
- 完善异常处理
- 添加日志系统
- 实现数据验证
- 优化代码结构

---

**恭喜完成 Day 4！API 功能已经很完善了！** 🎉
