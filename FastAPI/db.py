from sqlalchemy import create_engine,Column,Integer,String,Boolean,DateTime
from datetime import datetime, date, time, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
# engine
DATABASE_URL=settings.database_url
# SQLite特性需要指定check_same_thread=False
engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})

# create session class
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

# create base class
Base=declarative_base()

def default_tomorrow_9pm():
    """Return tomorrow 9:00 PM as datetime"""
    tomorrow = date.today() + timedelta(days=1)
    return datetime.combine(tomorrow, time(21, 0))  # 9:00 PM

# create mdoel class
class TodoDB(Base):
    __tablename__="todos"
    id=Column(Integer,primary_key=True,index=True)
    ddl=Column(DateTime, default=default_tomorrow_9pm)
    title=Column(String,index=True)
    done=Column(Boolean,default=False)

# create table
Base.metadata.create_all(bind=engine)
