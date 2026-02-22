from fastapi import FastAPI, Depends, Request, HTTPException, APIRouter, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from src.db.session import SessionLocal
from src.models.user import UserDB
from src.schemas.todo import TodoCreate, Todo, TodoUpdate, TodoListResponse
from src.schemas.pagination import PaginationParams
from src.schemas.user import UserCreate, UserLogin, User
from src.schemas.token import Token, TokenData
from src.core.logging import setup_logging, get_request_logger
import logging as std_logging
from src.core.exceptions import TodoNotFoundException, TodoValidationException, DatabaseException
from src.services import todo_service as services
from src.core.config import settings
from src.utils.email import send_todo_created_email

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from collections import defaultdict

from src.core.database_middleware import query_timer

limiter=Limiter(key_func=get_remote_address)



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

# Create dedicated file logger for timing logs
timing_file_logger = std_logging.getLogger("timing_logger")
timing_file_logger.setLevel(std_logging.INFO)
timing_file_logger.handlers.clear()
timing_file_handler = std_logging.FileHandler("/Users/Mac/code/project/FastAPI/app.log", mode='a')
timing_file_handler.setFormatter(std_logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
timing_file_logger.addHandler(timing_file_handler)
timing_file_logger.propagate = False

# Create v1 router for API versioning
router = APIRouter()


@app.middleware("http")
async def log_requests(request, call_next):
    request_logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    request_logger.info(f"Response:{response.status_code}")
    return response

from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Request timing middleware - measures request duration and logs slow requests
@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    import time
    
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Add timing header to response (helpful for debugging)
    response.headers["X-Request-Duration"] = f"{duration:.4f}s"
    
    # Log all requests with timing info
    from datetime import datetime
    import os
    log_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO timing_middleware Request timing | {request.method} {request.url.path} | Duration: {duration:.4f}s | Status: {response.status_code}\n"
    log_path = os.path.join(os.path.dirname(__file__), "app.log")
    with open(log_path, "a") as f:
        f.write(log_line)
    print(log_line.strip())
    
    # Warn about slow requests (e.g., > 1 second)
    SLOW_REQUEST_THRESHOLD = 1.0  # seconds
    if duration > SLOW_REQUEST_THRESHOLD:
        warning_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WARNING timing_middleware SLOW REQUEST DETECTED | {request.method} {request.url.path} | Duration: {duration:.4f}s | Status: {response.status_code} | Query: {request.query_params}\n"
        with open(log_path, "a") as f:
            f.write(warning_line)
        print(warning_line.strip())
    
    return response

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
    # CSP allows self + Swagger UI CDN + FastAPI favicon
    response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net https://fastapi.tiangolo.com 'unsafe-inline'"
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



# Import and include API router
from src.api.v1.api import api_router
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    # Note: Run migrations manually with: alembic upgrade head
    # Auto-migration disabled to prevent startup delays
    # from alembic.config import Config
    # from alembic import command
    # alembic_cfg=Config("alembic.ini")
    # command.upgrade(alembic_cfg,"head")
    
    logger.info("application startup complete")

