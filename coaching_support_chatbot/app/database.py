"""
Database engine and session factory.
Supports SQLite (local dev) and PostgreSQL (production).
"""
import pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import get_settings


def _make_engine():
    settings = get_settings()
    db_url = settings.database_url
    if settings.is_sqlite and db_url.startswith("sqlite:///./"):
        # Anchor relative SQLite db to coaching_support_chatbot folder
        base_dir = pathlib.Path(__file__).resolve().parent.parent
        rel_path = db_url.replace("sqlite:///./", "")
        db_url = f"sqlite:///{base_dir / rel_path}"

    connect_args = {"check_same_thread": False} if settings.is_sqlite else {}
    return create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
