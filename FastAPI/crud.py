from sqlalchemy.orm import Session, joinedload
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

def create_todo(db: Session, todo: TodoCreate,user_id:int) -> TodoDB:
    logger.info(f"Creating todo with title:{todo.title}")
    
    # Handle ddl field
    ddl_datetime = None
    if todo.ddl:
        try:
            ddl_datetime = datetime.strptime(todo.ddl, "%Y-%m-%d %H:%M")
        except ValueError:
            logger.warning(f"Invalid ddl format: {todo.ddl}, using default")
    
    db_todo = TodoDB(title=todo.title, done=False, ddl=ddl_datetime,owner_id=user_id)
    db.add(db_todo)
    db.flush()         
    db.refresh(db_todo)
    logger.debug(f"Todo created successfully in database with id:{db_todo.id}")
    return db_todo

def list_todos(db: Session,user_id:int,skip:int=0,limit:int=10,title:str|None=None,filter_today:bool=True,filter_week:bool=False,
               sort_by: str = "ddl", sort_order: str = "asc") -> tuple[list[TodoDB],int]:

    logger.debug(f"Listing all todos with pagination: skip={skip}, limit={limit},title={title},filter_today={filter_today},filter_week={filter_week},sort_by={sort_by},sort_order={sort_order}")
    
    # Use joinedload to prevent N+1 queries when accessing todo.owner
    query=db.query(TodoDB).options(
        joinedload(TodoDB.owner)  # Eager load owner relationship
    ).filter(TodoDB.owner_id==user_id)
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

def get_todo(db: Session, todo_id: int, user_id: int) -> TodoDB | None:
    """Get a single todo by ID and verify ownership"""
    return db.query(TodoDB).filter(TodoDB.id == todo_id, TodoDB.owner_id == user_id).first()

def update_todo(db: Session, todo_id: int, user_id: int, update: TodoUpdate) -> TodoDB | None:
    """Update a todo by ID and verify ownership"""
    # Get todo and verify ownership
    db_todo = db.query(TodoDB).filter(TodoDB.id == todo_id, TodoDB.owner_id == user_id).first()
    if not db_todo:
        return None
    
    # Update fields if provided
    if update.title is not None:
        db_todo.title = update.title
    if update.done is not None:
        db_todo.done = update.done
    if update.ddl is not None:
        if update.ddl == "":
            logger.debug("Clearing ddl")
            db_todo.ddl = None
        else:
            try:
                ddl_datetime = datetime.strptime(update.ddl, "%Y-%m-%d %H:%M")
                db_todo.ddl = ddl_datetime
                logger.debug(f"Updating ddl to: {update.ddl}")
            except ValueError:
                logger.warning(f"Invalid ddl format: {update.ddl}, keeping current value")

    db.flush()
    db.refresh(db_todo)
    logger.debug(f"Todo updated successfully: id={db_todo.id}, new_title='{db_todo.title}', new_done={db_todo.done}")
    return db_todo

def delete_todo(db: Session, todo_id: int, user_id: int) -> bool:
    """Delete a todo by ID and verify ownership"""
    db_todo = db.query(TodoDB).filter(TodoDB.id == todo_id, TodoDB.owner_id == user_id).first()
    if not db_todo:
        return False
    
    db.delete(db_todo)
    db.flush()
    logger.debug(f"Todo deleted successfully from database: id={db_todo.id}")
    return True





