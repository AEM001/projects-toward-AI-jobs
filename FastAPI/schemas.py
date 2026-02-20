from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional, ForwardRef
from enum import Enum

class SortField(str,Enum):
    id="id"
    ddl="ddl"
    title="title"
    done="done"

class SortOrder(str,Enum):
    asc="asc"
    desc="desc"

class PaginationParams(BaseModel):
    """Query parameters for pagination"""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of items to return")
    title: str | None = Field(default=None, description="Search by title (partial match)")
    filter_today: bool = Field(default=False, description="Show only todos due today")
    filter_week: bool = Field(default=False, description="Show only todos due within the next 7 days")

    sort_by: SortField = Field(default=SortField.ddl, description="Sort by field")
    sort_order: SortOrder = Field(default=SortOrder.asc, description="Sort order")

class PaginatedResponse(BaseModel):
    """Base pagination response metadata"""
    total: int = Field(description="Total number of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Number of items per page")
    page: int = Field(description="Current page number (0-based)")
    pages: int = Field(description="Total number of pages")

class TodoListResponse(PaginatedResponse):
    """Paginated response for todo lists"""
    items: "List[Todo]" = Field(description="List of todo items")

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

#Authentication schemas
class UserBase(BaseModel):
    email:str=Field(description="User email address")

class UserCreate(UserBase):
    password:str=Field(min_length=6,description="User password")

class UserLogin(UserBase):
    password:str=Field(description="User password")

class User(UserBase):
    id :int

    model_config=ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token:str=Field(description="JWT Access token")
    token_type:str=Field(default="bearer",description="Token type")

class TokenData(BaseModel):
    email:str | None=Field(default=None,description="User email from token")