from sqlalchemy.engine import Result
from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas import TodoCreate, TodoUpdate, Todo,TodoListResponse
from db import TodoDB
import crud
from datetime import datetime,date,timedelta

from log_config import setup_logging, get_request_logger
from exceptions import TodoNotFoundException, TodoValidationException, DatabaseException


logger=setup_logging(level="INFO",log_to_file=True)
request_logger=get_request_logger()

def create_todo_service(db: Session, todo: TodoCreate,user_id:int) -> Todo:
    """创建 Todo - 业务层"""
    logger.info(f"Creating todo with title:{todo.title} for user:{user_id} ")
    
    # Parse ddl if provided
    ddl_datetime = None
    if todo.ddl:
        try:
            ddl_datetime = datetime.strptime(todo.ddl, "%Y-%m-%d %H:%M")
        except ValueError:
            logger.warning(f"Invalid ddl format: {todo.ddl}, using None")
    
    db_todo=TodoDB(title=todo.title,ddl=ddl_datetime,owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    logger.info(f"Todo created successfully with id:{db_todo.id}")
    
    # Convert to response model with formatted ddl
    return Todo(
        id=db_todo.id,
        ddl=crud.format_datetime(db_todo.ddl),
        title=db_todo.title,
        done=db_todo.done,
        owner_id=db_todo.owner_id
    )


def list_todos_service(
    db: Session,
    user_id:int,
    skip:int=0,
    limit:int=10,
    title:str|None=None,
    filter_today:bool=False,
    filter_week:bool=False,
    sort_by: str = "ddl",
    sort_order: str = "asc") -> TodoListResponse:

    logger.info(f"--listing todos for user:{user_id} with filters and sorting:skip={skip},limit={limit},title={title},filter_today={filter_today},filter_week={filter_week},sort_by={sort_by},sort_order={sort_order}")
    # get paginated results and total count from CRUD
    todos,total=crud.list_todos(db,user_id=user_id,skip=skip,limit=limit,title=title,filter_today=filter_today,filter_week=filter_week,
                               sort_by=sort_by, sort_order=sort_order)
    logger.info(f"listed {len(todos)} todos out of {total} total")
    
    page=skip//limit if limit>0 else 0
    pages=max(1, (total+limit-1)//limit) if limit>0 else 1
    # Convert to response models with formatted ddl
    todo_items=[
        Todo(
            id=todo.id,
            ddl=crud.format_datetime(todo.ddl),
            title=todo.title,
            done=todo.done,
            owner_id=todo.owner_id
        )
        for todo in todos
    ]
    return TodoListResponse(
        items=todo_items,
        total=total,
        skip=skip,
        limit=limit,
        page=page,
        pages=pages
    )


def get_todo_service(db: Session, todo_id: int, user_id: int) -> Todo:
    """获取单个 Todo - 业务层"""
    logger.info(f"Getting todo with id:{todo_id} for user:{user_id}")
    
    # Get todo and verify ownership
    db_todo = crud.get_todo(db, todo_id, user_id)
    if not db_todo:
        logger.warning(f"Todo with id:{todo_id} not found for user:{user_id}")
        raise TodoNotFoundException(todo_id)
    
    logger.info(f"Todo retrieved successfully: {db_todo.title}")
    
    # Convert to response model with formatted ddl
    return Todo(
        id=db_todo.id,
        ddl=crud.format_datetime(db_todo.ddl),
        title=db_todo.title,
        done=db_todo.done,
        owner_id=db_todo.owner_id
    )


def update_todo_service(db: Session, todo_id: int, update: TodoUpdate, user_id: int) -> Todo:
    """更新 Todo - 不存在则抛出 404"""
    logger.info(f"Updating todo with id:{todo_id} for user:{user_id}")
    
    # Get existing todo and verify ownership
    existing_todo = crud.get_todo(db, todo_id, user_id)
    if not existing_todo:
        logger.warning(f"Todo with id:{todo_id} not found for user:{user_id}")
        raise TodoNotFoundException(todo_id)
    
    result=crud.update_todo(db,todo_id,user_id,update)
    if not result:
        logger.error(f"Failed to update todo with id:{todo_id}")
        raise DatabaseException("Failed to update todo")
    
    logger.info(f"Todo updated successfully: id:{todo_id}, title='{result.title}', done={result.done}")
    
    # Convert to response model with formatted ddl
    return Todo(
        id=result.id,
        ddl=crud.format_datetime(result.ddl),
        title=result.title,
        done=result.done,
        owner_id=result.owner_id
    )


def delete_todo_service(db: Session, todo_id: int, user_id: int) -> None:
    """删除 Todo - 业务层"""
    logger.info(f"Deleting todo with id:{todo_id} for user:{user_id}")
    
    # Get existing todo and verify ownership
    existing_todo = crud.get_todo(db, todo_id, user_id)
    if not existing_todo:
        logger.warning(f"Todo with id:{todo_id} not found for user:{user_id}")
        raise TodoNotFoundException(todo_id)
    
    # Delete todo
    success = crud.delete_todo(db, todo_id, user_id)
    if not success:
        logger.error(f"Failed to delete todo with id:{todo_id}")
        raise DatabaseException("Failed to delete todo")
    
    logger.info(f"Todo deleted successfully: {existing_todo.title}")


# ========================================
# 调试和实验服务
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
