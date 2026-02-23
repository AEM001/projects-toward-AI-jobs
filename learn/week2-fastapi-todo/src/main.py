from fastapi import FastAPI, HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from config.settings import settings
from logging import setup_logging
logger=setup_logging(level="INFO",log_to_file=True)
logger.info("FastAPI Todo app starting…")

from src.schemas.todo import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoListResponse,
    TodoStatus,
    TodoPriority
)
app=FastAPI(
    title=settings.app_name,
    description="A simple TODO management API",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

todos_db=[]
todo_id_counter=1

@app.get("/")
async def root():
    """Root path - API information"""
    return {
        "message": "Welcome to TODO API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return{"status":"OK"}

@app.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(todo: TodoCreate):
    """
    Create a new TODO task

    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional, max 1000 characters)
    - **priority**: Priority (low/medium/high, default medium)
    """
    global todo_id_counter

    # Create new task
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
    status: Optional[TodoStatus] = Query(None, description="Filter by status"),
    priority: Optional[TodoPriority] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return")
):
    """
    Get TODO list

    Supports filtering by status and priority, supports pagination
    """
    # Filter
    filtered_todos = todos_db

    if status:
        filtered_todos = [t for t in filtered_todos if t["status"] == status]

    if priority:
        filtered_todos = [t for t in filtered_todos if t["priority"] == priority]

    # Pagination
    paginated_todos = filtered_todos[skip : skip + limit]

    return {
        "todos": paginated_todos,
        "total": len(filtered_todos)
    }

@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    """
    Get a single TODO task by ID
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            return todo

    raise HTTPException(
        status_code=404,
        detail=f"Todo with id {todo_id} not found"
    )

@app.post("/todos")
async def create_todo(title:str,priority:str="medium"):
    global todo_id_counter
    new_todo={
        "id":todo_id_counter,
        "title":title,
        "priority":priority,
        "status":"pending"
    }
    
    todos_db.append(new_todo)
    todo_id_counter += 1
    return new_todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    """
    Update TODO task

    Only updates provided fields, unchanged fields remain the same
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            # Only update provided fields
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
    Delete TODO task
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
    """Application startup event"""
    print("🚀 FastAPI application started successfully!")
    print("📖 Visit http://localhost:8000/docs to view API documentation")

@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI Application closed")
    