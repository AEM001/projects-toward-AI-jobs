from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """初始化数据库，创建所有表"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
