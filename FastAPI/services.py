from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas import TodoCreate, TodoUpdate, Todo
from db import TodoDB
import crud


def create_todo_service(db: Session, todo: TodoCreate) -> TodoDB:
    """创建 Todo - 业务层"""
    return crud.create_todo(db, todo)


def list_todos_service(db: Session) -> list[TodoDB]:
    """获取所有 Todo - 业务层"""
    return crud.list_todos(db)


def get_todo_service(db: Session, id: int) -> TodoDB:
    """获取单个 Todo - 不存在则抛出 404"""
    todo = crud.get_todo(db, id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


def update_todo_service(db: Session, id: int, update: TodoUpdate) -> TodoDB:
    """更新 Todo - 不存在则抛出 404"""
    todo = crud.get_todo(db, id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud.update_todo(db, todo, update)


def delete_todo_service(db: Session, id: int) -> None:
    """删除 Todo - 不存在则抛出 404"""
    todo = crud.get_todo(db, id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    crud.delete_todo(db, todo)


# ========================================
# 🔬 调试和实验服务
# ========================================

def test_tx_fail_service(db: Session) -> None:
    """测试事务自动回滚 - 将领域异常转换为 HTTP 异常"""
    try:
        crud.test_tx_fail(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def test_tx_atomic_service(db: Session) -> dict:
    """测试原子性 - 多步操作中途失败应全部回滚"""
    # 第一步：创建一个 todo
    todo1 = TodoDB(title="atomic test 1", done=False)
    db.add(todo1)
    db.flush()
    
    # 第二步：再创建一个 todo
    todo2 = TodoDB(title="atomic test 2", done=False)
    db.add(todo2)
    db.flush()
    
    # 第三步：故意抛出异常
    raise HTTPException(status_code=400, detail="Atomic test: intentional failure")
