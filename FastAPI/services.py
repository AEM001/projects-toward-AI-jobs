from sqlalchemy.engine import Result
from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas import TodoCreate, TodoUpdate
from db import TodoDB
import crud

from log_config import setup_logging, get_request_logger
from exceptions import TodoNotFoundException, TodoValidationException, DatabaseException


logger=setup_logging(level="INFO",log_to_file=True)
request_logger=get_request_logger()

def create_todo_service(db: Session, todo: TodoCreate) -> TodoDB:
    """创建 Todo - 业务层"""
    logger.info(f"Creating todo with title:{todo.title}")
    result=crud.create_todo(db,todo)
    logger.info(f"Todo created successfully with id:{result.id}")
    return result


def list_todos_service(db: Session) -> list[TodoDB]:
    """获取所有 Todo - 业务层"""
    logger.info(f"--listing all todos")
    result=crud.list_todos(db)
    logger.info(f"listed {len(result)} todos")
    return result


def get_todo_service(db: Session, id: int) -> TodoDB:
    """获取单个 Todo - 不存在则抛出 404"""
    logger.info(f"--getting todo with id:{id}")
    todo = crud.get_todo(db, id)
    if todo is None:
        logger.warning(f"todo with id:{id} not found")
        raise TodoNotFoundException(id)
    logger.info(f"Todo found: {todo.title}")
    return todo


def update_todo_service(db: Session, id: int, update: TodoUpdate) -> TodoDB:
    """更新 Todo - 不存在则抛出 404"""
    logger.info(f"updating todo with id:{id}")
    todo = crud.get_todo(db, id)
    if todo is None:
        logger.warning(f"todo with id:{id} not found")
        raise TodoNotFoundException(id)
    result=crud.update_todo(db,todo,update)
    logger.info(f"todo updated: id{id},title='{result.title}',done={result.done}")
    return result


def delete_todo_service(db: Session, id: int) -> None:
    """删除 Todo - 不存在则抛出 404"""
    logger.info(f"deleting todo with id:{id}")
    todo = crud.get_todo(db, id)
    if todo is None:
        logger.warning(f"todo with id:{id} not found")
        raise TodoNotFoundException(id)
    crud.delete_todo(db, todo)
    logger.info(f"todo deleted successfully with id:{id}")


# ========================================
# 🔬 调试和实验服务
# ========================================

def test_tx_fail_service(db: Session) -> None:
    """测试事务自动回滚 - 将领域异常转换为 HTTP 异常"""
    logger.info("testing transaction fail")
    try:
        crud.test_tx_fail(db)
    except ValueError as e:
        logger.error(f"transaction failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def test_tx_atomic_service(db: Session) -> dict:
    """测试原子性 - 多步操作中途失败应全部回滚"""
    logger.info("testing transaction atomicity")
    # 第一步：创建一个 todo
    todo1 = TodoDB(title="atomic test 1", done=False)
    db.add(todo1)
    db.flush()
    
    # 第二步：再创建一个 todo
    todo2 = TodoDB(title="atomic test 2", done=False)
    db.add(todo2)
    db.flush()
    
    # 第三步：故意抛出异常
    logger.error("Atomic test: intentional failure")
    raise HTTPException(status_code=400, detail="Atomic test: intentional failure")
