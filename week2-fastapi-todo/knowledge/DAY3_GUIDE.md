# Day 3 Practical Guide: SQLite + SQLAlchemy ORM

## 🎯 Today's Goals

- Understand ORM (Object-Relational Mapping) concepts
- Configure SQLAlchemy database connection
- Create database models (ORM Model)
- Implement database session management
- Migrate from in-memory storage to SQLite

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ (Intermediate)

---

## 📚 Preparation (30 minutes)

### 1. Read Learning Materials

- [SQLAlchemy Official Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLite Basics](https://www.sqlite.org/docs.html)

### 2. Understand Core Concepts

#### What is ORM?

- **ORM (Object-Relational Mapping)** - Object-Relational Mapping
- Represent database tables with Python classes
- Use object operations instead of SQL statements
- Automatic data type conversion

#### SQLAlchemy Architecture

```
Application Layer (FastAPI)
    ↓
ORM Layer (SQLAlchemy Models)
    ↓
Core Layer (SQL Expression)
    ↓
Database (SQLite)
```

#### Schema vs Model (Important!)

- **Pydantic Schema**: Data validation and serialization at API layer
- **SQLAlchemy Model**: Table structure definition at database layer

```
API Request → Pydantic Schema → Business Logic → SQLAlchemy Model → Database
```

---

## 🛠️ Practical Steps

### Step 1: Configure Database Connection (30 minutes) ⭐ Core

Create `src/database/base.py`:

```python
"""
SQLAlchemy Base Model
"""
from sqlalchemy.ext.declarative import declarative_base

# Create base class, all ORM models inherit from this class
Base = declarative_base()
```

Create `src/database/connection.py`:

```python
"""
Database Connection Configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Database URL
# SQLite: sqlite:///./todo.db
# PostgreSQL: postgresql://user:password@localhost/dbname
DATABASE_URL = "sqlite:///./todo.db"

# Create database engine
# check_same_thread=False is specific to SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Print SQL statements during development
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Get database session (dependency injection)

    Use yield to ensure session is closed after request ends
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database
    Create all tables
    """
    from src.database.base import Base
    from src.models import todo  # Import all models

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
```

**Code Explanation**:

1. **create_engine** - Create database engine
2. **sessionmaker** - Create session factory
3. **get_db** - Dependency injection function, automatically manages session lifecycle
4. **init_db** - Create all database tables

### Step 2: Create ORM Models (40 minutes) ⭐ Core

Create `src/models/todo.py`:

```python
"""
Todo ORM Model
Define database table structure
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from src.database.base import Base


class TodoStatus(str, enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoPriority(str, enum.Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo(Base):
    """
    Todo ORM Model
    Corresponds to the todos table in the database
    """
    __tablename__ = "todos"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Task information
    title = Column(String(200), nullable=False, index=True)
    description = Column(String(1000), nullable=True)

    # Status and priority
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

    # Timestamps
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
        """String representation"""
        return f"<Todo(id={self.id}, title='{self.title}', status='{self.status.value}')>"
```

**Code Explanation**:

1. **__tablename__** - Specify table name
2. **Column** - Define columns
3. **primary_key** - Primary key
4. **index** - Create index, speed up queries
5. **nullable** - Whether NULL is allowed
6. **server_default** - Database-level default value
7. **func.now()** - Use database's current time function
8. **onupdate** - Automatically update timestamp on update

Create `src/models/__init__.py`:

```python
"""
Export all ORM models
"""
from src.models.todo import Todo, TodoStatus, TodoPriority

__all__ = ["Todo", "TodoStatus", "TodoPriority"]
```

### Step 3: Create Database Service Layer (40 minutes) ⭐ Core

Create `src/services/todo_service.py`:

```python
"""
Todo Business Logic Layer
Handle all Todo-related database operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from src.models.todo import Todo, TodoStatus, TodoPriority
from src.schemas.todo import TodoCreate, TodoUpdate


class TodoService:
    """Todo Service Class"""

    @staticmethod
    def create_todo(db: Session, todo: TodoCreate) -> Todo:
        """
        Create new Todo

        Args:
            db: Database session
            todo: Todo creation data

        Returns:
            Created Todo object
        """
        db_todo = Todo(
            title=todo.title,
            description=todo.description,
            priority=todo.priority,
            status=TodoStatus.PENDING
        )

        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)  # Refresh to get database-generated fields

        return db_todo

    @staticmethod
    def get_todo(db: Session, todo_id: int) -> Optional[Todo]:
        """
        Get Todo by ID

        Args:
            db: Database session
            todo_id: Todo ID

        Returns:
            Todo object or None
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
        Get Todo list

        Args:
            db: Database session
            status: Status filter
            priority: Priority filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Todo list
        """
        query = db.query(Todo)

        # Filters
        if status:
            query = query.filter(Todo.status == status)
        if priority:
            query = query.filter(Todo.priority == priority)

        # Pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_todos_count(
        db: Session,
        status: Optional[TodoStatus] = None,
        priority: Optional[TodoPriority] = None
    ) -> int:
        """
        Get total number of Todos

        Args:
            db: Database session
            status: Status filter
            priority: Priority filter

        Returns:
            Total number of Todos
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
        Update Todo

        Args:
            db: Database session
            todo_id: Todo ID
            todo_update: Update data

        Returns:
            Updated Todo object or None
        """
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

        if not db_todo:
            return None

        # Only update provided fields
        update_data = todo_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_todo, field, value)

        db.commit()
        db.refresh(db_todo)

        return db_todo

    @staticmethod
    def delete_todo(db: Session, todo_id: int) -> bool:
        """
        Delete Todo

        Args:
            db: Database session
            todo_id: Todo ID

        Returns:
            Whether deletion was successful
        """
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

        if not db_todo:
            return False

        db.delete(db_todo)
        db.commit()

        return True
```

**Code Explanation**:

1. **Static methods** - Use `@staticmethod`, no need to instantiate
2. **db.add()** - Add object to session
3. **db.commit()** - Commit transaction
4. **db.refresh()** - Refresh object to get database-generated values
5. **db.query()** - Create query
6. **filter()** - Add filter conditions
7. **first()** - Get first record
8. **all()** - Get all records
9. **count()** - Get record count

### Step 4: Update main.py to Use Database (40 minutes) ⭐ Core

Update `src/main.py`:

```python
"""
FastAPI TODO API Main Application
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
    description="TODO Management API using SQLite database",
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
    """Application startup event - Initialize database"""
    init_db()
    print("🚀 FastAPI application started successfully!")
    print("📖 Visit http://localhost:8000/docs to view API documentation")


@app.get("/")
async def root():
    """Root path"""
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
    """Create new TODO task"""
    return TodoService.create_todo(db, todo)


@app.get("/todos", response_model=TodoListResponse)
async def get_todos(
    status: Optional[TodoStatus] = Query(None, description="Filter by status"),
    priority: Optional[TodoPriority] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get TODO list"""
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
    """Get single TODO task"""
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
    """Update TODO task"""
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
    """Delete TODO task"""
    success = TodoService.delete_todo(db, todo_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found"
        )

    return {"message": "Todo deleted successfully"}
```

**Code Explanation**:

1. **Depends(get_db)** - Dependency injection, automatically manages database session
2. **startup_event** - Initialize database on application startup
3. **TodoService** - Use service layer to handle business logic
4. **Separation of concerns** - Route layer only handles HTTP, business logic in service layer

### Step 5: Test Database Functionality (20 minutes)

```bash
# 1. Start application (will automatically create database)
uvicorn src.main:app --reload

# 2. Create Todo
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn SQLAlchemy",
    "description": "Complete ORM tutorial",
    "priority": "high"
  }'

# 3. Get all Todos
curl "http://localhost:8000/todos"

# 4. Update Todo
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# 5. View database file
ls -lh todo.db

# 6. Use SQLite command line to view data
sqlite3 todo.db "SELECT * FROM todos;"
```

---

## ✅ Today's Achievements Check

### File Checklist

- [x] `src/database/base.py` - Base model
- [x] `src/database/connection.py` - Database connection
- [x] `src/models/todo.py` - ORM model
- [x] `src/services/todo_service.py` - Business logic
- [x] Updated `src/main.py` - API using database
- [x] `todo.db` - SQLite database file (auto-generated)

### Function Verification

```bash
# 1. Start application
uvicorn src.main:app --reload

# 2. Create data
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test database","priority":"high"}'

# 3. Restart application, data should still be there
# Ctrl+C to stop, then restart
uvicorn src.main:app --reload

# 4. Get data again
curl "http://localhost:8000/todos"
```

### Learning Outcomes

- [x] Understand ORM concepts
- [x] Learn to configure SQLAlchemy
- [x] Master creating ORM models
- [x] Learn to use dependency injection to manage database sessions
- [x] Understand service layer pattern
- [x] Master basic SQLAlchemy queries

---

## 💡 Common Questions

### Q1: What's the difference between ORM and writing SQL directly?

**A**: ORM uses object operations, safer and easier to maintain. Direct SQL is more flexible but error-prone.

### Q2: Why use dependency injection?

**A**: Automatically manages resource lifecycle, ensures database sessions are properly closed, avoids memory leaks.

### Q3: Where is the database file?

**A**: The `todo.db` file in the project root directory.

### Q4: How to view generated SQL?

**A**: Set `echo=True` in `create_engine`.

### Q5: How to reset the database?

**A**: Delete the `todo.db` file, restarting the application will automatically recreate it.

---

## 📝 Today's Summary

In Day 3, you completed:

1. ✅ Configured SQLAlchemy database connection
2. ✅ Created ORM models
3. ✅ Implemented service layer
4. ✅ Learned dependency injection
5. ✅ Implemented data persistence

**Tomorrow's Preview (Day 4)**:

- Complete all CRUD operations
- Optimize query performance
- Add more business logic
- Implement advanced filtering features

---

## 🎯 Homework (Optional)

1. **Add Indexes**: Add indexes for frequently queried fields
2. **Add Relationships**: Learn SQLAlchemy relationship mapping (one-to-many, many-to-many)
3. **View Database**: Use SQLite Browser to view database structure
4. **Performance Testing**: Create 1000 records, test query performance

---

**Congratulations on completing Day 3! Database integration complete!** 🎉
