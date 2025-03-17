from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Dynamic database path configuration
import sys
from pathlib import Path
from platformdirs import user_data_dir

if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.prefix != sys.base_prefix):
    data_dir = Path(sys.prefix) / 'todo_data'
else:
    data_dir = Path(user_data_dir('todo-cli'))

data_dir.mkdir(parents=True, exist_ok=True)
db_path = data_dir / 'todo.db'

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Add this at the bottom of the file after creating engine
from todo_cli import models  # Add this import
Base.metadata.create_all(bind=engine)