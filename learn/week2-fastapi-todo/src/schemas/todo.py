from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class TodoStatus(str,Enum):
    PENDING="pending"
    IN_PROGRESS="in_progress"
    DONE="done"

class TodoPriority(str,Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"

class TodoBase(BaseModel):
    title:str=Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title",
        example="Learn FastAPI"
    )
    description:Optional[str]=Field(
        None,
        max_length=1000,
        description="Task description",
        example="Complete the FastAPI tutorial"
    )
    priority:TodoPriority=Field(
        default=TodoPriority.MEDIUM,
        description="Task priority"
    )

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    """
    Request model for updating Todo
    All fields are optional
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Task title",
        example="Learn FastAPI"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Task description",
        example="Complete the FastAPI tutorial"
    )
    status: Optional[TodoStatus] = Field(
        None,
        description="Task status"
    )
    priority: Optional[TodoPriority] = Field(
        None,
        description="Task priority"
    )

class TodoResponse(TodoBase):
    """
    Todo response model
    Contains all fields including id and timestamps
    """
    id: int = Field(..., description="Task ID")
    status: TodoStatus = Field(default=TodoStatus.PENDING, description="Task status")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Update time")

    class Config:
        """Pydantic configuration"""
        from_attributes = True  # Allow creation from ORM model
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Learn FastAPI",
                "description": "Complete FastAPI tutorial",
                "status": "pending",
                "priority": "high",
                "created_at": "2024-12-20T10:00:00",
                "updated_at": "2024-12-20T10:00:00"
            }
        }

class TodoListResponse(BaseModel):
    """
    Todo list response model
    """
    todos: list[TodoResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "todos": [
                    {
                        "id": 1,
                        "title": "Learn FastAPI",
                        "description": "Complete tutorial",
                        "status": "pending",
                        "priority": "high",
                        "created_at": "2024-12-20T10:00:00",
                        "updated_at": "2024-12-20T10:00:00"
                    }
                ],
                "total": 1
            }
        }