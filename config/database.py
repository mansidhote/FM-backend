from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import tempfile, os

# Use a temporary directory for SQLite
db_dir = os.path.join(tempfile.gettempdir(), "finance_app")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "finance_app.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

import models  # Ensure models are imported for Alembic