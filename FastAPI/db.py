from sqlalchemy import create_engine,Column,Integer,String,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# engine
DATABASE_URL="sqlite:///./test.db"
# SQLite特性需要指定check_same_thread=False
engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})

# create session class
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)


# create base class
Base=declarative_base()

# create mdoel class
class TodoDB(Base):
    __tablename__="todos"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,index=True)
    done=Column(Boolean,default=False)

# create table
Base.metadata.create_all(bind=engine)
