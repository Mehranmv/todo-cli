from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    todo_body = Column(String)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    due_date = Column(DateTime(timezone=True))
    priority = Column(String)
    is_in_progress = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    complete_time = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Category", back_populates="todos")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    color = Column(String)
    todos = relationship("Todo", back_populates="category")


class ChangeHistory(Base):
    __tablename__ = "change_history"

    id = Column(Integer, primary_key=True, index=True)
    todo_id = Column(Integer, ForeignKey("todo.id"))
    change_description = Column(String)
    change_time = Column(DateTime(timezone=True), default=datetime.now)


class UserSetting(Base):
    __tablename__ = "user_setting"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    smtp_server = Column(String)
    smtp_port = Column(Integer)
    smtp_password = Column(String)
    reminder_time = Column(Integer, default=30)


class Setting(Base):
    __tablename__ = "setting"
    id = Column(Integer, primary_key=True, index=True)
    is_database_migrated = Column(Boolean, default=False)
