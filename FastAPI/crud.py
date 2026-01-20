from sqlalchemy.orm import Session
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

def get_todo(db: Session, id: int) -> TodoDB | None:
    """获取单个 Todo，不存在返回 None"""
    return db.query(TodoDB).filter(TodoDB.id == id).first()

def update_todo(db: Session, todo: TodoDB, update: TodoUpdate) -> TodoDB:
    """更新 Todo 对象（调用方需先查询）"""
    if update.title is not None:
        todo.title = update.title
    if update.done is not None:
        todo.done = update.done

    db.flush()
    db.refresh(todo)
    return todo

def delete_todo(db: Session, todo: TodoDB) -> None:
    """删除 Todo 对象（调用方需先查询）"""
    db.delete(todo)
    db.flush()

# ========================================
# 🔬 调试和实验函数
# ========================================

def test_tx_fail(db: Session) -> None:
    """测试事务自动回滚 - 失败案例（抛出普通异常）"""
    db.add(TodoDB(title="tx fail", done=False))
    db.flush()
    # 抛出异常会触发get_db_tx的rollback
    raise ValueError("force fail for testing")

def get_todo(db: Session, id:int)->TodoDB |None:
    return db.query(TodoDB).filter(TodoDB.id==id).first()

def get_todo_service(db:Session,id:int)->TodoDB:
    todo=get_todo(db,id)
    if(todo is None):
        raise HTTPException(status_code=404,detail="",)
    return todo

@app.get("/todos/{id}")
def get_todo(id:int,db=Depends(get_db)):
    return services.get_todo_service(db,id)