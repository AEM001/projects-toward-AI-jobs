# Day 4 Practical Guide: Enhance CRUD API + Advanced Features

## 🎯 Today's Goals
- Complete all CRUD operations
- Implement advanced query features (search, sorting)
- Add batch operations
- Optimize API response format
- Implement task statistics functionality

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ (Intermediate)

---

## 📚 Preparations Before Starting (30 minutes)

### 1. Read Learning Materials
- [RESTful API Design Best Practices](https://restfulapi.net/)
- [SQLAlchemy Advanced Queries](https://docs.sqlalchemy.org/en/20/orm/queryguide/)
- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)

### 2. Understand RESTful API Design Principles

#### HTTP Method Semantics
| Method | Purpose | Idempotent | Safe |
|------|------|--------|--------|
| GET | Get resource | ✅ | ✅ |
| POST | Create resource | ❌ | ❌ |
| PUT | Complete update | ✅ | ❌ |
| PATCH | Partial update | ❌ | ❌ |
| DELETE | Delete resource | ✅ | ❌ |

#### HTTP Status Codes
- **200 OK** - Success
- **201 Created** - Creation successful
- **204 No Content** - Deletion successful (no return content)
- **400 Bad Request** - Request error
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation failed

---

## 🛠️ Practical Steps

### Step 1: Extend Schema (30 minutes)

Update `src/schemas/todo.py`, add more features:

```python
"""
Extended Todo Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class TodoStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoPriority(str, Enum):
    """Task priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SortOrder(str, Enum):
    """Sort order"""
    ASC = "asc"
    DESC = "desc"


class TodoSortField(str, Enum):
    """Sortable fields"""
    ID = "id"
    TITLE = "title"
    PRIORITY = "priority"
    STATUS = "status"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TodoBase(BaseModel):
    """Todo base model"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Task description"
    )
    priority: TodoPriority = Field(
        default=TodoPriority.MEDIUM,
        description="Task priority"
    )


class TodoCreate(TodoBase):
    """Request model for creating Todo"""
    pass


class TodoUpdate(BaseModel):
    """Request model for updating Todo"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None


class TodoResponse(TodoBase):
    """Todo response model"""
    id: int
    status: TodoStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TodoListResponse(BaseModel):
    """Todo list response model"""
    todos: List[TodoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TodoStatsResponse(BaseModel):
    """Todo statistics response model"""
    total: int
    pending: int
    in_progress: int
    done: int
    high_priority: int
    medium_priority: int
    low_priority: int


class BatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int] = Field(..., min_items=1, description="List of IDs to delete")


class BatchDeleteResponse(BaseModel):
    """Batch delete response"""
    deleted_count: int
    failed_ids: List[int] = []
```

### Step 2: Extend Service Layer (40 minutes) ⭐ Core

Update `src/services/todo_service.py`:

```python
"""
Extended Todo Service Layer
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional, Tuple

from src.models.todo import Todo, TodoStatus, TodoPriority
from src.schemas.todo import TodoCreate, TodoUpdate, TodoSortField, SortOrder


class TodoService:
    """Todo service class"""
    
    @staticmethod
    def create_todo(db: Session, todo: TodoCreate) -> Todo:
        """Create a new Todo"""
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
        """Get Todo by ID"""
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
        Get Todo list (with search, sort, pagination)
        
        Returns:
            (todos, total_count)
        """
        query = db.query(Todo)
        
        # Filtering
        if status:
            query = query.filter(Todo.status == status)
        if priority:
            query = query.filter(Todo.priority == priority)
        
        # Search (title or description)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Todo.title.ilike(search_pattern),
                    Todo.description.ilike(search_pattern)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Sorting
        sort_column = getattr(Todo, sort_by.value)
        if sort_order == SortOrder.DESC:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Pagination
        todos = query.offset(skip).limit(limit).all()
        
        return todos, total
    
    @staticmethod
    def update_todo(
        db: Session,
        todo_id: int,
        todo_update: TodoUpdate
    ) -> Optional[Todo]:
        """Update Todo"""
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
        """Delete Todo"""
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        
        if not db_todo:
            return False
        
        db.delete(db_todo)
        db.commit()
        
        return True
    
    @staticmethod
    def batch_delete_todos(db: Session, todo_ids: List[int]) -> Tuple[int, List[int]]:
        """
        Batch delete Todos
        
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
        Get Todo statistics
        
        Returns:
            Statistics data dictionary
        """
        total = db.query(Todo).count()
        
        # Statistics by status
        pending = db.query(Todo).filter(Todo.status == TodoStatus.PENDING).count()
        in_progress = db.query(Todo).filter(Todo.status == TodoStatus.IN_PROGRESS).count()
        done = db.query(Todo).filter(Todo.status == TodoStatus.DONE).count()
        
        # Statistics by priority
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
        Delete all completed Todos
        
        Returns:
            Number of deleted items
        """
        deleted = db.query(Todo).filter(Todo.status == TodoStatus.DONE).delete()
        db.commit()
        
        return deleted
```

### Step 3: Update Routes (40 minutes) ⭐ Core

Update `src/main.py`:

```python
"""
Complete FastAPI TODO API
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
    description="Complete RESTful TODO Management API",
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
    """Application startup event"""
    init_db()
    print("🚀 FastAPI application started successfully!")


@app.get("/")
async def root():
    """Root path"""
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
    """Create a new TODO task"""
    return TodoService.create_todo(db, todo)


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
    """
    Get TODO list
    
    Supports filtering, searching, sorting, and pagination
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
    """Get TODO statistics"""
    return TodoService.get_stats(db)


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Get a single TODO task"""
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
    """Update TODO task"""
    todo = TodoService.update_todo(db, todo_id, todo_update)
    
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return todo


@app.delete("/todos/{todo_id}", status_code=204, tags=["Todos"])
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Delete TODO task"""
    success = TodoService.delete_todo(db, todo_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return None


@app.post("/todos/batch-delete", response_model=BatchDeleteResponse, tags=["Todos"])
async def batch_delete_todos(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db)
):
    """Batch delete TODO tasks"""
    deleted_count, failed_ids = TodoService.batch_delete_todos(db, request.ids)
    
    return {
        "deleted_count": deleted_count,
        "failed_ids": failed_ids
    }


@app.delete("/todos/completed/all", tags=["Todos"])
async def delete_completed_todos(db: Session = Depends(get_db)):
    """Delete all completed TODO tasks"""
    deleted_count = TodoService.delete_completed_todos(db)
    
    return {
        "message": f"Deleted {deleted_count} completed todos",
        "deleted_count": deleted_count
    }
```

### Step 4: Test Advanced Features (30 minutes)

```bash
# 1. Create test data
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Python","priority":"high"}'

curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI","priority":"medium"}'

# 2. Test search
curl "http://localhost:8000/todos?search=Python"

# 3. Test sorting
curl "http://localhost:8000/todos?sort_by=priority&sort_order=desc"

# 4. Test pagination
curl "http://localhost:8000/todos?page=1&page_size=5"

# 5. Test statistics
curl "http://localhost:8000/todos/stats"

# 6. Test batch delete
curl -X POST "http://localhost:8000/todos/batch-delete" \
  -H "Content-Type: application/json" \
  -d '{"ids":[1,2,3]}'

# 7. Delete completed tasks
curl -X DELETE "http://localhost:8000/todos/completed/all"
```

---

## ✅ Today's Results Check

### Feature Verification
- [x] Search function works
- [x] Sorting function works
- [x] Pagination function works
- [x] Statistics function works
- [x] Batch delete function works
- [x] Swagger documentation complete

### Learning Outcomes
- [x] Mastered advanced queries (search, sorting)
- [x] Learned to implement pagination
- [x] Understood batch operations
- [x] Mastered statistical queries
- [x] Learned to use tags to organize APIs

---

## 💡 Common Questions

### Q1: Why paginate?
**A**: Avoid returning too much data at once, improve performance and user experience.

### Q2: What's the difference between ilike and like?
**A**: `ilike` is case-insensitive fuzzy query, `like` is case-sensitive.

### Q3: How to optimize search performance?
**A**: Add indexes to search fields, use full-text search engines (like Elasticsearch).

---

## 📝 Today's Summary

On Day 4, you completed:
1. ✅ Implemented search functionality
2. ✅ Implemented sorting functionality
3. ✅ Implemented pagination functionality
4. ✅ Implemented statistics functionality
5. ✅ Implemented batch operations

**Tomorrow's Preview (Day 5)**:
- Improve exception handling
- Add logging system
- Implement data validation
- Optimize code structure

---

**Congratulations on completing Day 4! The API functionality is already very comprehensive!** 🎉
