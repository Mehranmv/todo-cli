from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base

class Todo(Base):
    __tablename__ = "todo"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    todo_body = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True))
    priority = Column(String)
    is_in_progress = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    complete_time = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, default=False)

class Setting(Base):
    __tablename__ = "setting"
    id = Column(Integer, primary_key=True, index=True)
    is_database_migrated = Column(Boolean, default=False)
