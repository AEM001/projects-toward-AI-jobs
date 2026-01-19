from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from db import SessionLocal
from schemas import TodoCreate, Todo, TodoUpdate
import crud
from fastapi import HTTPException

app = FastAPI(title="Simple Todo API")

# 读依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 写依赖：统一事务
def get_db_tx():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db_tx)):
    return crud.create_todo(db, todo)

@app.get("/todos", response_model=list[Todo])
def list_todos(db: Session = Depends(get_db)):
    return crud.list_todos(db)

@app.get("/todos/{id}", response_model=Todo)
def get_todo(id: int, db: Session = Depends(get_db)):
    return crud.get_todo_or_404(db, id)

@app.put("/todos/{id}", response_model=Todo)
def update_todo(id: int, update: TodoUpdate, db: Session = Depends(get_db_tx)):
    return crud.update_todo(db, id, update)

@app.delete("/todos/{id}", status_code=204)
def delete_todo(id: int, db: Session = Depends(get_db_tx)):
    crud.delete_todo(db, id)
    return

# ========================================
# 🔬 调试和实验路由
# ========================================

@app.post("/debug/tx-fail")
def tx_fail(db: Session = Depends(get_db_tx)):
    """测试事务自动回滚 - 失败案例"""
    return crud.test_tx_fail(db)
