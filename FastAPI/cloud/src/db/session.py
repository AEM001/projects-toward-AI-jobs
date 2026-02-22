from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# engine
DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# create session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
