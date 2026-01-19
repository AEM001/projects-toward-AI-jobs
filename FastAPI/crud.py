from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas import TodoCreate, TodoUpdate
from db import TodoDB

def create_todo(db: Session, todo: TodoCreate) -> TodoDB:
    db_todo = TodoDB(title=todo.title, done=False)
    db.add(db_todo)
    db.flush()          # 让 id 生成，但不提交（提交由 get_db_tx 做）
    db.refresh(db_todo)
    return db_todo

def list_todos(db: Session) -> list[TodoDB]:
    return db.query(TodoDB).order_by(TodoDB.id.asc()).all()

def get_todo_or_404(db: Session, id: int) -> TodoDB:
    db_todo = db.query(TodoDB).filter(TodoDB.id == id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

def update_todo(db: Session, id: int, update: TodoUpdate) -> TodoDB:
    db_todo = get_todo_or_404(db, id)

    if update.title is not None:
        db_todo.title = update.title
    if update.done is not None:
        db_todo.done = update.done

    db.flush()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, id: int) -> None:
    db_todo = get_todo_or_404(db, id)
    db.delete(db_todo)
    db.flush()

# ========================================
# 🔬 调试和实验函数
# ========================================

def test_tx_fail(db: Session) -> None:
    """测试事务自动回滚 - 失败案例"""
    db.add(TodoDB(title="tx fail", done=False))
    # 抛出异常会触发get_db_tx的rollback
    raise HTTPException(status_code=400, detail="force fail")
