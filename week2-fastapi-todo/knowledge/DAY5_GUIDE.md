# Day 5 实战指南：异常处理 + 日志系统 + 数据验证

## 🎯 今日目标
- 实现统一的异常处理
- 添加完整的日志系统
- 增强数据验证
- 添加请求/响应中间件
- 实现 API 限流（可选）

**预计时间**: 2-3 小时  
**难度**: ⭐⭐⭐ (中级)

---

## 📚 开始前的准备（30 分钟）

### 1. 阅读学习资料
- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python logging 模块](https://docs.python.org/3/library/logging.html)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)

---

## 🛠️ 实战步骤

### Step 1: 创建自定义异常（30 分钟）⭐ 核心

创建 `src/utils/exceptions.py`：

```python
"""
自定义异常类
"""
from fastapi import HTTPException, status


class TodoNotFoundException(HTTPException):
    """Todo 不存在异常"""
    def __init__(self, todo_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )


class TodoValidationException(HTTPException):
    """Todo 验证异常"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class DatabaseException(HTTPException):
    """数据库异常"""
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
```

### Step 2: 添加日志系统（40 分钟）⭐ 核心

创建 `src/utils/logger.py`：

```python
"""
日志配置
"""
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "fastapi_todo") -> logging.Logger:
    """
    配置日志系统
    
    Args:
        name: 日志器名称
        
    Returns:
        配置好的日志器
    """
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / "app.log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# 创建全局日志器
logger = setup_logger()
```

### Step 3: 添加请求日志中间件（30 分钟）

创建 `src/utils/middleware.py`：

```python
"""
自定义中间件
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """
        记录每个请求的信息
        """
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(
            f"Response: {response.status_code} "
            f"- Time: {process_time:.3f}s"
        )
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

### Step 4: 增强数据验证（30 分钟）

更新 `src/schemas/todo.py`，添加自定义验证器：

```python
from pydantic import field_validator
import re


class TodoCreate(TodoBase):
    """创建 Todo 的请求模型"""
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """验证标题"""
        # 去除首尾空格
        v = v.strip()
        
        # 检查是否为空
        if not v:
            raise ValueError('标题不能为空')
        
        # 检查是否包含非法字符
        if re.search(r'[<>]', v):
            raise ValueError('标题不能包含 < 或 > 字符')
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """验证描述"""
        if v:
            v = v.strip()
            if not v:
                return None
        return v
```

### Step 5: 更新 main.py 集成所有功能（40 分钟）⭐ 核心

更新 `src/main.py`：

```python
"""
完整的 FastAPI TODO API（带异常处理和日志）
"""
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import math

from src.database.connection import get_db, init_db
from src.schemas.todo import *
from src.services.todo_service import TodoService
from src.utils.logger import logger
from src.utils.middleware import RequestLoggingMiddleware
from src.utils.exceptions import TodoNotFoundException, DatabaseException

app = FastAPI(
    title="TODO API",
    description="完整的 RESTful TODO 管理 API（带异常处理和日志）",
    version="1.0.0",
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)


# 全局异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "请求数据验证失败"
        }
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理数据库错误"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "数据库错误",
            "message": "服务器内部错误，请稍后重试"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误",
            "message": "发生未知错误，请联系管理员"
        }
    )


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    try:
        init_db()
        logger.info("🚀 FastAPI 应用启动成功！")
        logger.info("📖 访问 http://localhost:8000/docs 查看 API 文档")
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("👋 FastAPI 应用已关闭")


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    logger.info("访问根路径")
    return {
        "message": "Welcome to TODO API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/todos", response_model=TodoResponse, status_code=201, tags=["Todos"])
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
):
    """创建新的 TODO 任务"""
    try:
        logger.info(f"创建 Todo: {todo.title}")
        result = TodoService.create_todo(db, todo)
        logger.info(f"Todo 创建成功: ID={result.id}")
        return result
    except Exception as e:
        logger.error(f"创建 Todo 失败: {str(e)}")
        raise DatabaseException("创建任务失败")


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
    """获取 TODO 列表"""
    try:
        logger.info(f"获取 Todo 列表: page={page}, page_size={page_size}")
        
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
        
        logger.info(f"返回 {len(todos)} 条 Todo，总计 {total} 条")
        
        return {
            "todos": todos,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"获取 Todo 列表失败: {str(e)}")
        raise DatabaseException("获取任务列表失败")


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """获取单个 TODO 任务"""
    logger.info(f"获取 Todo: ID={todo_id}")
    
    todo = TodoService.get_todo(db, todo_id)
    
    if not todo:
        logger.warning(f"Todo 不存在: ID={todo_id}")
        raise TodoNotFoundException(todo_id)
    
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db)
):
    """更新 TODO 任务"""
    try:
        logger.info(f"更新 Todo: ID={todo_id}")
        
        todo = TodoService.update_todo(db, todo_id, todo_update)
        
        if not todo:
            logger.warning(f"Todo 不存在: ID={todo_id}")
            raise TodoNotFoundException(todo_id)
        
        logger.info(f"Todo 更新成功: ID={todo_id}")
        return todo
    except TodoNotFoundException:
        raise
    except Exception as e:
        logger.error(f"更新 Todo 失败: {str(e)}")
        raise DatabaseException("更新任务失败")


@app.delete("/todos/{todo_id}", status_code=204, tags=["Todos"])
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """删除 TODO 任务"""
    try:
        logger.info(f"删除 Todo: ID={todo_id}")
        
        success = TodoService.delete_todo(db, todo_id)
        
        if not success:
            logger.warning(f"Todo 不存在: ID={todo_id}")
            raise TodoNotFoundException(todo_id)
        
        logger.info(f"Todo 删除成功: ID={todo_id}")
        return None
    except TodoNotFoundException:
        raise
    except Exception as e:
        logger.error(f"删除 Todo 失败: {str(e)}")
        raise DatabaseException("删除任务失败")
```

---

## ✅ 今日成果检查

### 文件清单
- [x] `src/utils/exceptions.py` - 自定义异常
- [x] `src/utils/logger.py` - 日志系统
- [x] `src/utils/middleware.py` - 中间件
- [x] 更新的 `src/main.py` - 集成所有功能
- [x] `logs/app.log` - 日志文件（自动生成）

### 功能验证
```bash
# 1. 启动应用，观察日志
uvicorn src.main:app --reload

# 2. 测试正常请求（查看日志）
curl "http://localhost:8000/todos"

# 3. 测试验证错误
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"<invalid>"}'

# 4. 测试 404 错误
curl "http://localhost:8000/todos/999"

# 5. 查看日志文件
cat logs/app.log
```

### 学习收获
- [x] 掌握自定义异常
- [x] 学会配置日志系统
- [x] 理解中间件机制
- [x] 掌握全局异常处理
- [x] 学会增强数据验证

---

## 📝 今日总结

在 Day 5，你完成了：
1. ✅ 实现了统一异常处理
2. ✅ 添加了完整日志系统
3. ✅ 实现了请求日志中间件
4. ✅ 增强了数据验证
5. ✅ 提升了代码健壮性

**明天预告（Day 6）**：
- 编写完整的 API 测试
- 创建 Postman 测试集合
- 运行测试覆盖率分析

---

**恭喜完成 Day 5！应用已经很健壮了！** 🎉
