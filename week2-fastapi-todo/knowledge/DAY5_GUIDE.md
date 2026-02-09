# Day 5 Practical Guide: Exception Handling + Logging System + Data Validation

## 🎯 Today's Goals

- Implement unified exception handling
- Add complete logging system
- Enhance data validation
- Add request/response middleware
- Implement API rate limiting (optional)

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ (Intermediate)

---

## 📚 Preparation (30 minutes)

### 1. Read Learning Materials

- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python logging module](https://docs.python.org/3/library/logging.html)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)

---

## 🛠️ Practical Steps

### Step 1: Create Custom Exceptions (30 minutes) ⭐ Core

Create `src/utils/exceptions.py`:

```python
"""
Custom exception classes
"""
from fastapi import HTTPException, status


class TodoNotFoundException(HTTPException):
    """Todo not found exception"""
    def __init__(self, todo_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )


class TodoValidationException(HTTPException):
    """Todo validation exception"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class DatabaseException(HTTPException):
    """Database exception"""
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
```

### Step 2: Add Logging System (40 minutes) ⭐ Core

Create `src/utils/logger.py`:

```python
"""
Logging configuration
"""
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "fastapi_todo") -> logging.Logger:
    """
    Configure logging system

    Args:
        name: Logger name

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Log format
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
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


# Create global logger
logger = setup_logger()
```

### Step 3: Add Request Logging Middleware (30 minutes)

Create `src/utils/middleware.py`:

```python
"""
Custom middleware
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""

    async def dispatch(self, request: Request, call_next):
        """
        Log information for each request
        """
        start_time = time.time()

        # Log request info
        logger.info(f"Request: {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response info
        logger.info(
            f"Response: {response.status_code} "
            f"- Time: {process_time:.3f}s"
        )

        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)

        return response
```

### Step 4: Enhance Data Validation (30 minutes)

Update `src/schemas/todo.py`, add custom validators:

```python
from pydantic import field_validator
import re


class TodoCreate(TodoBase):
    """Todo creation request model"""

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title"""
        # Remove leading/trailing whitespace
        v = v.strip()

        # Check if empty
        if not v:
            raise ValueError('Title cannot be empty')

        # Check for illegal characters
        if re.search(r'[<>]', v):
            raise ValueError('Title cannot contain < or > characters')

        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate description"""
        if v:
            v = v.strip()
            if not v:
                return None
        return v
```

### Step 5: Update main.py to Integrate All Features (40 minutes) ⭐ Core

Update `src/main.py`:

```python
"""
Complete FastAPI TODO API (with exception handling and logging)
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
    description="Complete RESTful TODO Management API (with exception handling and logging)",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Request data validation failed"
        }
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database error",
            "message": "Internal server error, please try again later"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "Unknown error occurred, please contact administrator"
        }
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    try:
        init_db()
        logger.info("🚀 FastAPI application started successfully!")
        logger.info("📖 Visit http://localhost:8000/docs to view API documentation")
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("👋 FastAPI application has been shut down")


@app.get("/", tags=["Root"])
async def root():
    """Root path"""
    logger.info("Accessing root path")
    return {
        "message": "Welcome to TODO API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/todos", response_model=TodoResponse, status_code=201, tags=["Todos"])
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
):
    """Create new TODO task"""
    try:
        logger.info(f"Creating Todo: {todo.title}")
        result = TodoService.create_todo(db, todo)
        logger.info(f"Todo created successfully: ID={result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create Todo: {str(e)}")
        raise DatabaseException("Failed to create task")


@app.get("/todos", response_model=TodoListResponse, tags=["Todos"])
async def get_todos(
    status: Optional[TodoStatus] = Query(None, description="Filter by status"),
    priority: Optional[TodoPriority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search title or description"),
    sort_by: TodoSortField = Query(TodoSortField.CREATED_AT, description="Sort field"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get TODO list"""
    try:
        logger.info(f"Getting Todo list: page={page}, page_size={page_size}")

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

        logger.info(f"Returning {len(todos)} Todos, total {total}")

        return {
            "todos": todos,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Failed to get Todo list: {str(e)}")
        raise DatabaseException("Failed to get task list")


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Get single TODO task"""
    logger.info(f"Getting Todo: ID={todo_id}")

    todo = TodoService.get_todo(db, todo_id)

    if not todo:
        logger.warning(f"Todo not found: ID={todo_id}")
        raise TodoNotFoundException(todo_id)

    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db)
):
    """Update TODO task"""
    try:
        logger.info(f"Updating Todo: ID={todo_id}")

        todo = TodoService.update_todo(db, todo_id, todo_update)

        if not todo:
            logger.warning(f"Todo not found: ID={todo_id}")
            raise TodoNotFoundException(todo_id)

        logger.info(f"Todo updated successfully: ID={todo_id}")
        return todo
    except TodoNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to update Todo: {str(e)}")
        raise DatabaseException("Failed to update task")


@app.delete("/todos/{todo_id}", status_code=204, tags=["Todos"])
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Delete TODO task"""
    try:
        logger.info(f"Deleting Todo: ID={todo_id}")

        success = TodoService.delete_todo(db, todo_id)

        if not success:
            logger.warning(f"Todo not found: ID={todo_id}")
            raise TodoNotFoundException(todo_id)

        logger.info(f"Todo deleted successfully: ID={todo_id}")
        return None
    except TodoNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete Todo: {str(e)}")
        raise DatabaseException("Failed to delete task")
```

---

## ✅ Today's Results Check

### File Checklist

- [x] `src/utils/exceptions.py` - Custom exceptions
- [x] `src/utils/logger.py` - Logging system
- [x] `src/utils/middleware.py` - Middleware
- [x] Updated `src/main.py` - Integrate all features
- [x] `logs/app.log` - Log file (auto-generated)

### Function Verification

```bash
# 1. Start application, observe logs
uvicorn src.main:app --reload

# 2. Test normal requests (check logs)
curl "http://localhost:8000/todos"

# 3. Test validation errors
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"<invalid>"}'

# 4. Test 404 errors
curl "http://localhost:8000/todos/999"

# 5. View log file
cat logs/app.log
```

### Learning Outcomes

- [x] Master custom exceptions
- [x] Learn to configure logging system
- [x] Understand middleware mechanism
- [x] Master global exception handling
- [x] Learn to enhance data validation

---

## 📝 Today's Summary

On Day 5, you completed:

1. ✅ Implemented unified exception handling
2. ✅ Added complete logging system
3. ✅ Implemented request logging middleware
4. ✅ Enhanced data validation
5. ✅ Improved code robustness

**Tomorrow's Preview (Day 6)**:

- Write complete API tests
- Create Postman test collections
- Run test coverage analysis

---

**Congratulations on completing Day 5! The application is now very robust!** 🎉
