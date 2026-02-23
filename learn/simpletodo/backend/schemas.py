from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# 用户相关 Schema
class UserCreate(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# 任务相关 Schema
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
