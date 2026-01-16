from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
import os
from dotenv import load_dotenv

from database import init_db, get_session
from models import User
from schemas import (
    UserCreate, UserRead, UserLogin, Token,
    TaskCreate, TaskUpdate, TaskRead
)
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from crud import create_task, get_tasks_by_user, get_task, update_task, delete_task

load_dotenv()

app = FastAPI(title="Task Manager API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """应用启动时初始化数据库"""
    init_db()


@app.get("/")
def root():
    """欢迎信息"""
    return {"message": "Task Manager API - Go to /docs for API documentation"}


# ==================== 认证相关 API ====================

@app.post("/auth/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    """用户注册"""
    from sqlmodel import select

    # 检查邮箱是否已存在
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 创建用户
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=Token)
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    """用户登录，返回 JWT token"""
    user = authenticate_user(session, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== 任务相关 API ====================

@app.get("/tasks", response_model=List[TaskRead])
def read_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取当前用户的所有任务"""
    return get_tasks_by_user(session, current_user.id)


@app.post("/tasks", response_model=TaskRead)
def create_new_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """创建新任务"""
    return create_task(session, task, current_user.id)


@app.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取单个任务"""
    db_task = get_task(session, task_id, current_user.id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_existing_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """更新任务"""
    db_task = update_task(session, task_id, current_user.id, task_update)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


@app.delete("/tasks/{task_id}")
def delete_existing_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """删除任务"""
    success = delete_task(session, task_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return {"message": "Task deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
