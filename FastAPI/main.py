from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from db import SessionLocal
from schemas import TodoCreate, Todo, TodoUpdate
import services

from log_config import setup_logging, get_request_logger
from fastapi.responses import JSONResponse
from exceptions import TodoNotFoundException,TodoValidationException,DatabaseException

app = FastAPI(title="Simple Todo API")

logger=setup_logging(level="DEBUG",log_to_file=True)#or INFO
request_logger = get_request_logger()

@app.middleware("http")
async def log_requests(request,call_next):
    request_logger.info(f"Request: {request.method} {request.url}")
    response=await call_next(request)
    request_logger.info(f"Response:{response.status_code}")
    return response

@app.exception_handler(TodoNotFoundException)
async def todo_not_found_handler(request, exc):
    logger.warning(f"Todo with id {exc.todo_id} not found")
    return JSONResponse(
        status_code=404,
        content={"detail": f"Todo with id {exc.todo_id} not found"}
    )

@app.exception_handler(TodoValidationException)
async def todo_validation_handler(request, exc):
    logger.warning(f"Todo validation failed: {exc.detail}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail}
    )

@app.exception_handler(DatabaseException)
async def database_exception_handler(request, exc):
    logger.error(f"Database operation failed: {exc.detail}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed"}
    )



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
    return services.create_todo_service(db, todo)

@app.get("/todos", response_model=list[Todo])
def list_todos(db: Session = Depends(get_db)):
    return services.list_todos_service(db)

@app.get("/todos/{id}", response_model=Todo)
def get_todo(id: int, db: Session = Depends(get_db)):
    return services.get_todo_service(db, id)

@app.put("/todos/{id}", response_model=Todo)
def update_todo(id: int, update: TodoUpdate, db: Session = Depends(get_db_tx)):
    return services.update_todo_service(db, id, update)

@app.delete("/todos/{id}", status_code=204)
def delete_todo(id: int, db: Session = Depends(get_db_tx)):
    services.delete_todo_service(db, id)


# ========================================
# 🔬 调试和实验路由
# ========================================

@app.post("/debug/tx-fail")
def tx_fail(db: Session = Depends(get_db_tx)):
    """测试事务自动回滚 - 失败案例"""
    services.test_tx_fail_service(db)

@app.post("/debug/tx-atomic")
def tx_atomic(db: Session = Depends(get_db_tx)):
    """测试原子性 - 多步操作中途失败应全部回滚"""
    return services.test_tx_atomic_service(db)

@app.on_event("startup")
async def startup_event():
    logger.info("application startup complete -database tables created")
