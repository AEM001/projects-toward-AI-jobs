from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base, default_tomorrow_9pm

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    ddl = Column(DateTime, default=default_tomorrow_9pm, index=True)
    title = Column(String, index=True)
    done = Column(Boolean, default=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    owner = relationship("UserDB", back_populates="todos")

    __table_args__ = (Index('ix_todos_owner_id_ddl', 'owner_id', 'ddl'),)