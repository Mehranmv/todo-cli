from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime


class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True))
    title = Column(String)
    todo_body = Column(String)
    priority = Column(String)
    is_in_progress = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    complete_time = Column(DateTime(timezone=True))
