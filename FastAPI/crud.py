from sqlalchemy.orm import Session
from schemas import TodoCreate, TodoUpdate
from db import TodoDB
from datetime import datetime,date,timedelta
import logging
logger = logging.getLogger("fastapi_todo.crud")

def format_datetime(dt: datetime | None) -> str | None:
    """Format datetime to string without seconds"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M")

def create_todo(db: Session, todo: TodoCreate) -> TodoDB:
    logger.info(f"Creating todo with title:{todo.title}")
    
    # Handle ddl field
    ddl_datetime = None
    if todo.ddl:
        try:
            ddl_datetime = datetime.strptime(todo.ddl, "%Y-%m-%d %H:%M")
        except ValueError:
            logger.warning(f"Invalid ddl format: {todo.ddl}, using default")
    
    db_todo = TodoDB(title=todo.title, done=False, ddl=ddl_datetime)
    db.add(db_todo)
    db.flush()          # 让 id 生成，但不提交（提交由 get_db_tx 做）
    db.refresh(db_todo)
    logger.debug(f"Todo created successfully in database with id:{db_todo.id}")
    return db_todo

def list_todos(db: Session,skip:int=0,limit:int=10,title:str|None=None,filter_today:bool=True,filter_week:bool=False,
               sort_by: str = "ddl", sort_order: str = "asc") -> tuple[list[TodoDB],int]:

    logger.debug(f"Listing all todos with pagination: skip={skip}, limit={limit},title={title},filter_today={filter_today},filter_week={filter_week},sort_by={sort_by},sort_order={sort_order}")
    query=db.query(TodoDB)
    if title:
        query=query.filter(TodoDB.title.ilike(f"%{title}%"))
    if filter_today:
        today = date.today()
        query = query.filter(TodoDB.ddl >= datetime.combine(today, datetime.min.time()),
                           TodoDB.ddl < datetime.combine(today + timedelta(days=1), datetime.min.time()))
    if filter_week:
        today = date.today()
        week_end = today + timedelta(days=7)
        query = query.filter(TodoDB.ddl <= datetime.combine(week_end, datetime.max.time()))
    
    total=query.count()
    sort_column=getattr(TodoDB,sort_by)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()
    
    # Handle nulls for ddl column (put nulls last)
    if sort_by == "ddl":
        sort_column = sort_column.nulls_last()
    todos=query.order_by(sort_column).offset(skip).limit(limit).all()
    logger.debug(f"found{len(todos)}todos out of {total}total")
    return todos,total

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
    if update.ddl is not None:
        if update.ddl == "":
            logger.debug("Clearing ddl")
            todo.ddl = None
        else:
            try:
                ddl_datetime = datetime.strptime(update.ddl, "%Y-%m-%d %H:%M")
                todo.ddl = ddl_datetime
                logger.debug(f"Updating ddl to: {update.ddl}")
            except ValueError:
                logger.warning(f"Invalid ddl format: {update.ddl}, keeping current value")

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





