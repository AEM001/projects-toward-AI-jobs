from fastapi import FastAPI, Depends, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from db import SessionLocal
from schemas import TodoCreate, Todo, TodoUpdate,TodoListResponse ,PaginationParams
from log_config import setup_logging, get_request_logger
from exceptions import TodoNotFoundException, TodoValidationException, DatabaseException
import services
from config import settings

tags_metadata = [
    {
        "name": "Todos",
        "description": "Operations for managing TODO tasks"
    },
    {
        "name": "Health",
        "description": "Health check and monitoring endpoints"
    },
    {
        "name": "Debug",
        "description": "Debugging and testing endpoints"
    }
]


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    contact={
            "name": "Albert",
            "email": "transcendence0915@gmail.com"
        },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=tags_metadata
)

from fastapi.middleware.cors import CORSMiddleware
# Add middleware after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cor_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cor_allow_headers,
)

logger = setup_logging(level="DEBUG" if settings.debug_mode else "INFO", log_to_file=True)
request_logger = get_request_logger()
# Create v1 router for API versioning
router = APIRouter()


@app.middleware("http")
async def log_requests(request, call_next):
    request_logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
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

@router.post("/todos", 
          response_model=Todo, 
          status_code=201, 
          tags=["Todos"],
          summary="Create a new TODO task",
          description="""
Create a new TODO task with the provided information.

The task will be created with a default status of 'pending' and current timestamp."""
# """",
#           responses={
#               201: {
#                   "description": "Todo created successfully",
#                   "content": {
#                       "application/json": {
#                           "example": {
#                               "id": 1,
#                               "title": "Learn FastAPI",
#                               "description": "Complete the tutorial",
#                               "status": "pending",
#                               "created_at": "2024-01-01T12:00:00",
#                               "updated_at": "2024-01-01T12:00:00"
#                           }
#                       }
#                   }
#               },
#               422: {"description": "Validation error"}}
          )
def create_todo(todo: TodoCreate, db: Session = Depends(get_db_tx)):
    return services.create_todo_service(db, todo)

@router.get("/todos", response_model=TodoListResponse, tags=["Todos"], 
           summary="List all TODO tasks with pagination and filtering",
           description="""
Retrieve a paginated list of all TODO tasks in the system with optional filtering.
 
**Query Parameters:**
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 10, max: 100)
- `title`: Search by title (partial match)
- `filter_today`: Show only todos due today (default: false)
- `filter_week`: Show only todos due within the next 7 days (default: false)
 
**Returns:** Paginated list with metadata including total count, current page, etc.
""",
responses={
    200: {
        "description": "Paginated and filtered list of todos",
        "content": {
            "application/json": {
                "example": {
                    "items": [
                        {"id": 1, "title": "Buy groceries", "ddl": "2026-02-10 12:00", "done": False}
                    ],
                    "total": 5,
                    "skip": 0,
                    "limit": 10,
                    "page": 0,
                    "pages": 1
                }
            }
        }
    }
})
def list_todos(Pagination: PaginationParams=Depends(),db: Session = Depends(get_db)):
    return services.list_todos_service(
        db,skip=Pagination.skip,limit=Pagination.limit,
        title=Pagination.title,
        filter_today=Pagination.filter_today,
        filter_week=Pagination.filter_week,
        sort_by=Pagination.sort_by.value,
        sort_order=Pagination.sort_order.value)

@router.get("/todos/{id}", response_model=Todo,tags=["Todos"],summary="Get a specific TODO task",
 description="""
Retrieve a single TODO task by its unique identifier.
 
**Path Parameters:**
- `id`: The unique identifier of the todo task
 
**Returns:** The complete todo object if found
""",
         responses={
             200: {
                 "description": "Todo found",
                 "content": {
                     "application/json": {
                         "example": {
                             "id": 1,
                             "title": "Learn FastAPI",
                             "description": "Complete tutorial",
                             "status": "pending",
                             "created_at": "2024-01-01T12:00:00",
                             "updated_at": "2024-01-01T12:00:00"
                         }
                     }
                 }
             },
             404: {
                 "description": "Todo not found",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Todo with id 1 not found"}
                     }
                 }
             }
         })
def get_todo(id: int, db: Session = Depends(get_db)):
    return services.get_todo_service(db, id)

@router.put("/todos/{id}", response_model=Todo, tags=["Todos"], summary="Update an existing TODO task",
description="""
Update an existing TODO task with new information.

**Path Parameters:**
- `id`: The unique identifier of the todo task

**Request Body:**
- `update`: Partial update data for the todo (title, description, status)

**Returns:** The updated todo object
""",
responses={
    200: {
        "description": "Todo updated successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "title": "Learn FastAPI",
                    "description": "Complete tutorial",
                    "status": "completed",
                    "created_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T12:30:00"
                }
            }
        }
    },
    404: {
        "description": "Todo not found",
        "content": {
            "application/json": {
                "example": {"detail": "Todo with id 1 not found"}
            }
        }
    }
})
def update_todo(id: int, update: TodoUpdate, db: Session = Depends(get_db_tx)):
    return services.update_todo_service(db, id, update)

@router.delete("/todos/{id}", status_code=204, tags=["Todos"], summary="Delete a TODO task",
description="""
Delete a TODO task by its unique identifier.

**Path Parameters:**
- `id`: The unique identifier of the todo task to delete

This operation cannot be undone.
""",
responses={
    204: {
        "description": "Todo deleted successfully"
    },
    404: {
        "description": "Todo not found",
        "content": {
            "application/json": {
                "example": {"detail": "Todo with id 1 not found"}
            }
        }
    }
})
def delete_todo(id: int, db: Session = Depends(get_db_tx)):
    services.delete_todo_service(db, id)


# ========================================
# 🔬 调试和实验路由
# ========================================

@app.post("/debug/tx-fail", tags=["Debug"], summary="Test transaction failure",
description="Test automatic rollback on transaction failure",
responses={
    500: {
        "description": "Internal server error due to transaction failure"
    }
})
def tx_fail(db: Session = Depends(get_db_tx)):
    """测试事务自动回滚 - 失败案例"""
    services.test_tx_fail_service(db)

@app.post("/debug/tx-atomic", tags=["Debug"], summary="Test transaction atomicity",
description="Test atomicity - all operations in transaction succeed or all fail",
responses={
    200: {
        "description": "Transaction succeeded"
    },
    500: {
        "description": "Transaction failed and rolled back"
    }
})
def tx_atomic(db: Session = Depends(get_db_tx)):
    """测试原子性 - 多步操作中途失败应全部回滚"""
    return services.test_tx_atomic_service(db)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("application startup complete -database tables created")
