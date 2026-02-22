from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address
from collections import defaultdict

from src.db.session import SessionLocal
from src.models.user import UserDB
from src.schemas.token import TokenData
from src.core.config import settings

security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)

# Rate limiting
failed_attempts = defaultdict(list)
BLOCK_DURATION = timedelta(minutes=15)
MAX_FAILED_ATTEMPTS = 5

def is_ip_blocked(client_ip: str) -> bool:
    now = datetime.utcnow()
    attempts = failed_attempts.get(client_ip, [])
    recent_attempts = [attempt for attempt in attempts if now - attempt < BLOCK_DURATION]
    failed_attempts[client_ip] = recent_attempts
    return len(recent_attempts) >= MAX_FAILED_ATTEMPTS

def record_failed_attempt(client_ip: str):
    failed_attempts[client_ip].append(datetime.utcnow())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

def get_user(db: Session, email: str):
    return db.query(UserDB).filter(UserDB.email == email).first()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
