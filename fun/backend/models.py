from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """用户模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)


class Task(SQLModel, table=True):
    """任务模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending")  # pending, in_progress, completed
    created_at: datetime = Field(default_factory=datetime.now)

    user_id: int = Field(foreign_key="user.id")
