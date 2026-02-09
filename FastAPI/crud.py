from sqlalchemy.orm import Session
from schemas import TodoCreate, TodoUpdate
from db import TodoDB
import logging
logger = logging.getLogger("fastapi_todo.crud")

def create_todo(db: Session, todo: TodoCreate) -> TodoDB:
    logger.info(f"Creating todo with title:{todo.title}")
    db_todo = TodoDB(title=todo.title, done=False)
    db.add(db_todo)
    db.flush()          # 让 id 生成，但不提交（提交由 get_db_tx 做）
    db.refresh(db_todo)
    logger.debug(f"Todo created successfully in database with id:{db_todo.id}")
    return db_todo

def list_todos(db: Session) -> list[TodoDB]:
    logger.debug("Listing all todos")
    return db.query(TodoDB).order_by(TodoDB.id.asc()).all()

def get_todo(db: Session, id: int) -> TodoDB | None:
    """获取单个 Todo，不存在返回 None"""
    logger.debug(f"Getting todo with id:{id}")
    return db.query(TodoDB).filter(TodoDB.id == id).first()

def update_todo(db: Session, todo: TodoDB, update: TodoUpdate) -> TodoDB:
    """更新 Todo 对象（调用方需先查询）"""
    logger.debug(f"Updating todo in database: id={todo.id}, current_title='{todo.title}', current_done={todo.done}")
    if update.title is not None:
        logger.debug(f"Updating title to: '{update.title}'")
        todo.title = update.title
    if update.done is not None:
        logger.debug(f"Updating done status to: {update.done}")
        todo.done = update.done

    db.flush()
    db.refresh(todo)
    logger.debug(f"Todo updated successfully: id={todo.id}, new_title='{todo.title}', new_done={todo.done}")
    return todo

def delete_todo(db: Session, todo: TodoDB) -> None:
    """删除 Todo 对象（调用方需先查询）"""
    logger.debug(f"Deleting todo from database: id={todo.id}, title='{todo.title}'")
    db.delete(todo)
    db.flush()
    logger.debug(f"Todo deleted successfully from database: id={todo.id}")

# ========================================
# 🔬 调试和实验函数
# ========================================

def test_tx_fail(db: Session) -> None:
    """测试事务自动回滚 - 失败案例（抛出普通异常）"""
    db.add(TodoDB(title="tx fail", done=False))
    db.flush()
    # 抛出异常会触发get_db_tx的rollback
    raise ValueError("force fail for testing")





