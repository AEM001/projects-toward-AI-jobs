from fastapi import FastAPI, Depends, Request, HTTPException, APIRouter, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from db import SessionLocal,UserDB
from schemas import TodoCreate, Todo, TodoUpdate,TodoListResponse ,PaginationParams,UserCreate,UserLogin,User,Token,TokenData
from log_config import setup_logging, get_request_logger
from exceptions import TodoNotFoundException, TodoValidationException, DatabaseException
import services
from config import settings


from passlib.context import CryptContext
from jose import JWTError,jwt
from datetime import datetime, timedelta

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from collections import defaultdict

limiter=Limiter(key_func=get_remote_address)

# use redis in production
failed_attempts=defaultdict(list)
BLOCK_DURATION=timedelta(minutes=15)
MAX_FAILED_ATTEMPTS=5


def is_ip_blocked(client_ip: str) -> bool:
    now = datetime.utcnow()
    attempts = failed_attempts.get(client_ip, [])

    # remove old attempts
    recent_attempts = [attempt for attempt in attempts if now - attempt < BLOCK_DURATION]
    failed_attempts[client_ip] = recent_attempts

    return len(recent_attempts) >= MAX_FAILED_ATTEMPTS

def record_failed_attempt(client_ip: str):
    failed_attempts[client_ip].append(datetime.utcnow())

#
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security=HTTPBearer()

SECRET_KEY=settings.secret_key
ALGORITHM=settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=settings.access_token_expire_minutes

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, email: str):
    return db.query(UserDB).filter(UserDB.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



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

app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)




from fastapi.middleware.cors import CORSMiddleware
# Add middleware after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
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

from fastapi.middleware.trustedhost import TrustedHostMiddleware

# security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Add trusted host middleware for production
if not settings.debug_mode:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "www.yourdomain.com"]  # Replace with your actual domains
    )


from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Add this after your other middleware
if not settings.debug_mode:
    app.add_middleware(HTTPSRedirectMiddleware)

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

async def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security),db:Session=Depends(get_db)):
    credentials_exception=HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        token=credentials.credentials
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email:str=payload.get("sub")
        if email is None:
            raise credentials_exception

        token_data=TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user=get_user(db,email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


@router.post("/todos", 
          response_model=Todo, 
          status_code=201, 
          tags=["Todos"],
          summary="Create a new TODO task",
          description="""
Create a new TODO task with the provided information.

The task will be created with a default status of 'pending' and current timestamp."""
          )
@limiter.limit("20/minute")
def create_todo(request: Request, todo: TodoCreate,current_user:User=Depends(get_current_user),db: Session = Depends(get_db_tx)):
    return services.create_todo_service(db, todo,current_user.id)


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
"""
# responses={
#     200: {
#         "description": "Paginated and filtered list of todos",
#         "content": {
#             "application/json": {
#                 "example": {
#                     "items": [
#                         {"id": 1, "title": "Buy groceries", "ddl": "2026-02-10 12:00", "done": False}
#                     ],
#                     "total": 5,
#                     "skip": 0,
#                     "limit": 10,
#                     "page": 0,
#                     "pages": 1
#                 }
#             }
#         }
#     }
# }
)
@limiter.limit("100/minute")
def list_todos(request: Request, Pagination: PaginationParams=Depends(),current_user:User=Depends(get_current_user),db: Session = Depends(get_db)):
    return services.list_todos_service(
        db,skip=Pagination.skip,limit=Pagination.limit,
        title=Pagination.title,
        filter_today=Pagination.filter_today,
        filter_week=Pagination.filter_week,
        sort_by=Pagination.sort_by.value,
        sort_order=Pagination.sort_order.value,
        user_id=current_user.id)

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
def get_todo(id: int, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    return services.get_todo_service(db, id,current_user.id)

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
def update_todo(id: int, update: TodoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_tx)):
    return services.update_todo_service(db, id, update, current_user.id)

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
def delete_todo(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_tx)):
    services.delete_todo_service(db, id, current_user.id)


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
    from alembic.config import Config
    from alembic import command

    alembic_cfg=Config("alembic.ini")
    command.upgrade(alembic_cfg,"head")

    logger.info("application startup complete -database tables created")


@app.post("/auth/register",response_model=User,tags=["Authentication"])
def register(user:UserCreate,db:Session=Depends(get_db)):
    db_user=get_user(db,user.email)
    if db_user:
        raise HTTPException(status_code=400,detail="Email has been registered")
    
    hashed_password=get_password_hash(user.password)
    db_user=UserDB(email=user.email,hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login",response_model=Token, tags=["Authentication"])
@limiter.limit("5/minute")
def login(request:Request,user_credentials:UserLogin,db:Session=Depends(get_db)):
    client_ip=get_remote_address(request)
    if is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts"
        )
    user=authenticate_user(db,user_credentials.email,user_credentials.password)
    if not user:
        record_failed_attempt(client_ip)
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate":"Bearer"}
        )

    if client_ip in failed_attempts:
        del failed_attempts[client_ip]
    
    access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token=create_access_token(
        data={"sub":user.email},
        expires_delta=access_token_expires
    )
    return {"access_token":access_token,"token_type":"bearer"}

@app.get("/auth/me",response_model=User,tags=["Authentication"])
def get_current_user_info(credentials:HTTPAuthorizationCredentials=Depends(security),db:Session=Depends(get_db)):
    token=credentials.credentials
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email:str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401,detail="Cound not validate credentials")
        token_data=TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=401,detail="Could not validate credentials")

    user=get_user(db,email=token_data.email)
    if user is None:
        raise HTTPException(status_code=404,detail="User not found")
    return user

