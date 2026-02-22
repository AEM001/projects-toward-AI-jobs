from fastapi import APIRouter
from .endpoints import todos, auth, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(todos.router, tags=["Todos"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
