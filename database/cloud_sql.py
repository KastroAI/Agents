"""Cloud SQL (PostgreSQL) engine and session configuration."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings

engine = create_engine(
    settings.CLOUD_SQL_CONNECTION_STRING,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for use as a FastAPI dependency.

    Ensures the session is closed after the request completes.

    Yields:
        A SQLAlchemy :class:`Session`.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
