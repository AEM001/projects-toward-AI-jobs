from fastapi import FastAPI, Depends, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from db import SessionLocal
from schemas import TodoCreate, Todo, TodoUpdate
from log_config import setup_logging, get_request_logger
from exceptions import TodoNotFoundException, TodoValidationException, DatabaseException
import services

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


app = FastAPI(title="Simple Todo API",
description="""
 A production-ready TODO management API built with FastAPI.
    
    ## Features
    
    * **CRUD Operations**: Create, read, update, delete tasks
    * **Data Validation**: Automatic validation with Pydantic
    * **Logging**: Comprehensive logging across all layers
    * **Error Handling**: Proper error responses and exception handling
    * **Request Validation**: Content-type and size validation
    * **API Versioning**: Versioned endpoints at `/api/v1/*`
    
    ## Getting Started
    
    1. Create a task: `POST /todos` or `POST /api/v1/todos`
    2. List tasks: `GET /todos` or `GET /api/v1/todos`
    3. Update a task: `PUT /todos/{id}` or `PUT /api/v1/todos/{id}`
    4. Delete a task: `DELETE /todos/{id}` or `DELETE /api/v1/todos/{id}`
    """,
    version="1.0.0",
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
logger = setup_logging(level="DEBUG", log_to_file=True)
request_logger = get_request_logger()

class RequestValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Validate Content-Type for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                logger.warning(f"Invalid Content-Type: {content_type}")
                raise HTTPException(
                    status_code=400,
                    detail="Content-Type must be application/json"
                )

        # Check request body size (limit to 1MB)
        body = await request.body()
        if len(body) > 1024 * 1024:  # 1MB limit
            logger.warning(f"Request body too large: {len(body)} bytes")
            raise HTTPException(
                status_code=413,
                detail="Request body too large (max 1MB)"
            )

        response = await call_next(request)
        return response


# Add middleware after app creation
app.add_middleware(RequestValidationMiddleware)


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

@router.get("/todos", response_model=list[Todo],tags=["Todos"],summary="List all TODO tasks",
description="""
Retrieve a list of all TODO tasks in the system.
 
Returns all tasks ordered by creation date.
""",
responses={
             200: {
                 "description": "List of todos",
                 "content": {
                     "application/json": {
                         "example": [
                             {
                                 "id": 1,
                                 "title": "Learn FastAPI",
                                 "status": "pending"
                             }
                         ]
                     }
                 }
             }
         }
)
def list_todos(db: Session = Depends(get_db)):
    return services.list_todos_service(db)

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
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("application startup complete -database tables created")
