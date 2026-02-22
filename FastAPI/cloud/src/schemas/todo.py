from pydantic import BaseModel, Field, ConfigDict
from typing import List
from .pagination import PaginatedResponse

class TodoListResponse(PaginatedResponse):
    """Paginated response for todo lists"""
    items: List["Todo"] = Field(description="List of todo items")

    model_config = ConfigDict(from_attributes=True)

class TodoCreate(BaseModel):
    title:str=Field(min_length=1,description="Todo title, cannot be empty")
    ddl:str|None=Field(default=None, description="Deadline in format 'YYYY-MM-DD HH:MM', defaults to tomorrow 9PM")

class Todo(BaseModel):
    model_config=ConfigDict(from_attributes=True)#允许从ORM对象读取属性
    
    id:int
    ddl:str
    title:str
    done:bool
    owner_id:int

class TodoUpdate(BaseModel):
    ddl: str | None = Field(default=None, description="Update task deadline, leave empty to not modify, format: 'YYYY-MM-DD HH:MM'", json_schema_extra={"example": "2024-02-11 21:00"})
    title: str | None = Field(default=None, description="Update task title, leave empty to not modify", json_schema_extra={"example": None})
    done: bool | None = Field(default=None, description="Update task status, leave empty to not modify", json_schema_extra={"example": None})
