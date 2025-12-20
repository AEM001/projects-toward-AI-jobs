# Day 3 实战指南：SQLite + SQLAlchemy ORM

## 🎯 今日目标
- 理解 ORM（对象关系映射）概念
- 配置 SQLAlchemy 数据库连接
- 创建数据库模型（ORM Model）
- 实现数据库会话管理
- 将内存存储迁移到 SQLite

**预计时间**: 2-3 小时  
**难度**: ⭐⭐⭐ (中级)

---

## 📚 开始前的准备（30 分钟）

### 1. 阅读学习资料
- [SQLAlchemy 官方教程](https://docs.sqlalchemy.org/en/20/tutorial/)
- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLite 基础](https://www.sqlite.org/docs.html)

### 2. 理解核心概念

#### 什么是 ORM？
- **ORM (Object-Relational Mapping)** - 对象关系映射
- 用 Python 类表示数据库表
- 用对象操作代替 SQL 语句
- 自动处理数据类型转换

#### SQLAlchemy 架构
```
应用层 (FastAPI)
    ↓
ORM 层 (SQLAlchemy Models)
    ↓
Core 层 (SQL Expression)
    ↓
数据库 (SQLite)
```

#### Schema vs Model（重要！）
- **Pydantic Schema**: API 层的数据验证和序列化
- **SQLAlchemy Model**: 数据库层的表结构定义

```
API 请求 → Pydantic Schema → 业务逻辑 → SQLAlchemy Model → 数据库
```

---

## 🛠️ 实战步骤

### Step 1: 配置数据库连接（30 分钟）⭐ 核心

创建 `src/database/base.py`：

```python
"""
SQLAlchemy Base 模型
"""
from sqlalchemy.ext.declarative import declarative_base

# 创建基类，所有 ORM 模型都继承这个类
Base = declarative_base()
```

创建 `src/database/connection.py`：

```python
"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# 数据库 URL
# SQLite: sqlite:///./todo.db
# PostgreSQL: postgresql://user:password@localhost/dbname
DATABASE_URL = "sqlite:///./todo.db"

# 创建数据库引擎
# check_same_thread=False 是 SQLite 特有的配置
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # 开发时打印 SQL 语句
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（依赖注入）
    
    使用 yield 确保会话在请求结束后关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表
    """
    from src.database.base import Base
    from src.models import todo  # 导入所有模型
    
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功！")
```

**代码讲解**：
1. **create_engine** - 创建数据库引擎
2. **sessionmaker** - 创建会话工厂
3. **get_db** - 依赖注入函数，自动管理会话生命周期
4. **init_db** - 创建所有数据库表

### Step 2: 创建 ORM 模型（40 分钟）⭐ 核心

创建 `src/models/todo.py`：

```python
"""
Todo ORM 模型
定义数据库表结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from src.database.base import Base


class TodoStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoPriority(str, enum.Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo(Base):
    """
    Todo ORM 模型
    对应数据库中的 todos 表
    """
    __tablename__ = "todos"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 任务信息
    title = Column(String(200), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    
    # 状态和优先级
    status = Column(
        SQLEnum(TodoStatus),
        default=TodoStatus.PENDING,
        nullable=False,
        index=True
    )
    priority = Column(
        SQLEnum(TodoPriority),
        default=TodoPriority.MEDIUM,
        nullable=False,
        index=True
    )
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        """字符串表示"""
        return f"<Todo(id={self.id}, title='{self.title}', status='{self.status.value}')>"
```

**代码讲解**：
1. **__tablename__** - 指定表名
2. **Column** - 定义列
3. **primary_key** - 主键
4. **index** - 创建索引，加快查询
5. **nullable** - 是否允许 NULL
6. **server_default** - 数据库级别的默认值
7. **func.now()** - 使用数据库的当前时间函数
8. **onupdate** - 更新时自动更新时间戳

创建 `src/models/__init__.py`：

```python
"""
导出所有 ORM 模型
"""
from src.models.todo import Todo, TodoStatus, TodoPriority

__all__ = ["Todo", "TodoStatus", "TodoPriority"]
```

### Step 3: 创建数据库服务层（40 分钟）⭐ 核心

创建 `src/services/todo_service.py`：

```python
"""
Todo 业务逻辑层
处理所有 Todo 相关的数据库操作
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from src.models.todo import Todo, TodoStatus, TodoPriority
from src.schemas.todo import TodoCreate, TodoUpdate


class TodoService:
    """Todo 服务类"""
    
    @staticmethod
    def create_todo(db: Session, todo: TodoCreate) -> Todo:
        """
        创建新的 Todo
        
        Args:
            db: 数据库会话
            todo: Todo 创建数据
            
        Returns:
            创建的 Todo 对象
        """
        db_todo = Todo(
            title=todo.title,
            description=todo.description,
            priority=todo.priority,
            status=TodoStatus.PENDING
        )
        
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)  # 刷新以获取数据库生成的字段
        
        return db_todo
    
    @staticmethod
    def get_todo(db: Session, todo_id: int) -> Optional[Todo]:
        """
        根据 ID 获取 Todo
        
        Args:
            db: 数据库会话
            todo_id: Todo ID
            
        Returns:
            Todo 对象或 None
        """
        return db.query(Todo).filter(Todo.id == todo_id).first()
    
    @staticmethod
    def get_todos(
        db: Session,
        status: Optional[TodoStatus] = None,
        priority: Optional[TodoPriority] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Todo]:
        """
        获取 Todo 列表
        
        Args:
            db: 数据库会话
            status: 状态筛选
            priority: 优先级筛选
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            Todo 列表
        """
        query = db.query(Todo)
        
        # 筛选
        if status:
            query = query.filter(Todo.status == status)
        if priority:
            query = query.filter(Todo.priority == priority)
        
        # 分页
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_todos_count(
        db: Session,
        status: Optional[TodoStatus] = None,
        priority: Optional[TodoPriority] = None
    ) -> int:
        """
        获取 Todo 总数
        
        Args:
            db: 数据库会话
            status: 状态筛选
            priority: 优先级筛选
            
        Returns:
            Todo 总数
        """
        query = db.query(Todo)
        
        if status:
            query = query.filter(Todo.status == status)
        if priority:
            query = query.filter(Todo.priority == priority)
        
        return query.count()
    
    @staticmethod
    def update_todo(
        db: Session,
        todo_id: int,
        todo_update: TodoUpdate
    ) -> Optional[Todo]:
        """
        更新 Todo
        
        Args:
            db: 数据库会话
            todo_id: Todo ID
            todo_update: 更新数据
            
        Returns:
            更新后的 Todo 对象或 None
        """
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        
        if not db_todo:
            return None
        
        # 只更新提供的字段
        update_data = todo_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_todo, field, value)
        
        db.commit()
        db.refresh(db_todo)
        
        return db_todo
    
    @staticmethod
    def delete_todo(db: Session, todo_id: int) -> bool:
        """
        删除 Todo
        
        Args:
            db: 数据库会话
            todo_id: Todo ID
            
        Returns:
            是否删除成功
        """
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        
        if not db_todo:
            return False
        
        db.delete(db_todo)
        db.commit()
        
        return True
```

**代码讲解**：
1. **静态方法** - 使用 `@staticmethod`，不需要实例化
2. **db.add()** - 添加对象到会话
3. **db.commit()** - 提交事务
4. **db.refresh()** - 刷新对象，获取数据库生成的值
5. **db.query()** - 创建查询
6. **filter()** - 添加过滤条件
7. **first()** - 获取第一条记录
8. **all()** - 获取所有记录
9. **count()** - 获取记录数

### Step 4: 更新 main.py 使用数据库（40 分钟）⭐ 核心

更新 `src/main.py`：

```python
"""
FastAPI TODO API 主应用
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from src.database.connection import get_db, init_db
from src.schemas.todo import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoListResponse,
    TodoStatus,
    TodoPriority
)
from src.services.todo_service import TodoService

app = FastAPI(
    title="TODO API",
    description="使用 SQLite 数据库的 TODO 管理 API",
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
    """应用启动事件 - 初始化数据库"""
    init_db()
    print("🚀 FastAPI 应用启动成功！")
    print("📖 访问 http://localhost:8000/docs 查看 API 文档")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to TODO API with SQLite",
        "version": "1.0.0",
        "database": "SQLite"
    }


@app.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
):
    """创建新的 TODO 任务"""
    return TodoService.create_todo(db, todo)


@app.get("/todos", response_model=TodoListResponse)
async def get_todos(
    status: Optional[TodoStatus] = Query(None, description="按状态筛选"),
    priority: Optional[TodoPriority] = Query(None, description="按优先级筛选"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的最大记录数"),
    db: Session = Depends(get_db)
):
    """获取 TODO 列表"""
    todos = TodoService.get_todos(db, status, priority, skip, limit)
    total = TodoService.get_todos_count(db, status, priority)
    
    return {
        "todos": todos,
        "total": total
    }


@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """获取单个 TODO 任务"""
    todo = TodoService.get_todo(db, todo_id)
    
    if not todo:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found"
        )
    
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db)
):
    """更新 TODO 任务"""
    todo = TodoService.update_todo(db, todo_id, todo_update)
    
    if not todo:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found"
        )
    
    return todo


@app.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """删除 TODO 任务"""
    success = TodoService.delete_todo(db, todo_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found"
        )
    
    return {"message": "Todo deleted successfully"}
```

**代码讲解**：
1. **Depends(get_db)** - 依赖注入，自动管理数据库会话
2. **startup_event** - 应用启动时初始化数据库
3. **TodoService** - 使用服务层处理业务逻辑
4. **分离关注点** - 路由层只处理 HTTP，业务逻辑在服务层

### Step 5: 测试数据库功能（20 分钟）

```bash
# 1. 启动应用（会自动创建数据库）
uvicorn src.main:app --reload

# 2. 创建 Todo
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "学习 SQLAlchemy",
    "description": "完成 ORM 教程",
    "priority": "high"
  }'

# 3. 获取所有 Todo
curl "http://localhost:8000/todos"

# 4. 更新 Todo
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# 5. 查看数据库文件
ls -lh todo.db

# 6. 使用 SQLite 命令行查看数据
sqlite3 todo.db "SELECT * FROM todos;"
```

---

## ✅ 今日成果检查

### 文件清单
- [x] `src/database/base.py` - Base 模型
- [x] `src/database/connection.py` - 数据库连接
- [x] `src/models/todo.py` - ORM 模型
- [x] `src/services/todo_service.py` - 业务逻辑
- [x] 更新的 `src/main.py` - 使用数据库的 API
- [x] `todo.db` - SQLite 数据库文件（自动生成）

### 功能验证
```bash
# 1. 启动应用
uvicorn src.main:app --reload

# 2. 创建数据
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试数据库","priority":"high"}'

# 3. 重启应用，数据应该还在
# Ctrl+C 停止，然后重新启动
uvicorn src.main:app --reload

# 4. 再次获取数据
curl "http://localhost:8000/todos"
```

### 学习收获
- [x] 理解 ORM 概念
- [x] 学会配置 SQLAlchemy
- [x] 掌握创建 ORM 模型
- [x] 学会使用依赖注入管理数据库会话
- [x] 理解服务层模式
- [x] 掌握基本的 SQLAlchemy 查询

---

## 💡 常见问题

### Q1: ORM 和直接写 SQL 有什么区别？
**A**: ORM 用对象操作，更安全、更易维护。直接 SQL 更灵活，但容易出错。

### Q2: 为什么要用依赖注入？
**A**: 自动管理资源生命周期，确保数据库会话正确关闭，避免内存泄漏。

### Q3: 数据库文件在哪里？
**A**: 项目根目录的 `todo.db` 文件。

### Q4: 如何查看生成的 SQL？
**A**: 在 `create_engine` 中设置 `echo=True`。

### Q5: 如何重置数据库？
**A**: 删除 `todo.db` 文件，重启应用会自动重新创建。

---

## 📝 今日总结

在 Day 3，你完成了：
1. ✅ 配置了 SQLAlchemy 数据库连接
2. ✅ 创建了 ORM 模型
3. ✅ 实现了服务层
4. ✅ 学会了依赖注入
5. ✅ 实现了数据持久化

**明天预告（Day 4）**：
- 完善所有 CRUD 操作
- 优化查询性能
- 添加更多业务逻辑
- 实现高级筛选功能

---

## 🎯 作业（可选）

1. **添加索引**: 为常用查询字段添加索引
2. **添加关系**: 学习 SQLAlchemy 的关系映射（一对多、多对多）
3. **查看数据库**: 使用 SQLite Browser 查看数据库结构
4. **性能测试**: 创建 1000 条数据，测试查询性能

---

**恭喜完成 Day 3！数据库集成完成！** 🎉
