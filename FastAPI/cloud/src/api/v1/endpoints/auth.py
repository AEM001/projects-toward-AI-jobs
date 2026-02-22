from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter

from src.api.deps import get_db, get_current_user, limiter, is_ip_blocked, record_failed_attempt, failed_attempts
from src.schemas.user import UserCreate, UserLogin, User
from src.schemas.token import Token
from src.models.user import UserDB
from src.core.security import verify_password, get_password_hash, create_access_token, authenticate_user
from src.core.config import settings
from slowapi.util import get_remote_address
from datetime import timedelta
from jose import JWTError, jwt
from src.schemas.token import TokenData

router = APIRouter()

@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    from src.api.deps import get_user
    db_user = get_user(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email has been registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    from src.api.deps import get_user
    
    client_ip = get_remote_address(request)
    if is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts"
        )
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        record_failed_attempt(client_ip)
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if client_ip in failed_attempts:
        del failed_attempts[client_ip]
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
