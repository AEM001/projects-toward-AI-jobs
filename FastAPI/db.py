from sqlalchemy import create_engine,Column,Integer,String,Boolean,DateTime,ForeignKey,Index
from datetime import datetime, date, time, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from config import settings

# engine
DATABASE_URL=settings.database_url

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
    ddl=Column(DateTime, default=default_tomorrow_9pm,index=True)
    title=Column(String,index=True)
    done=Column(Boolean,default=False,index=True)
    owner_id=Column(Integer,ForeignKey("users.id"),index=True)
    owner=relationship("UserDB",back_populates="todos")

    __table_args__=(Index('ix_todos_owner_id_ddl','owner_id','ddl'),)

class UserDB(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,nullable=False)
    hashed_password=Column(String,nullable=False)
    todos=relationship("TodoDB",back_populates="owner")
    # balance=Column(Integer,default=0)
# # create table
# Base.metadata.create_all(bind=engine)
