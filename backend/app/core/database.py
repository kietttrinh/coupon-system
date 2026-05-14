"""
Database configuration and session management for the Coupon System.

This module handles:
- SQLAlchemy engine creation with MySQL connection
- Session factory for database operations
- Base declarative class for ORM models
- Dependency function to provide database sessions to API endpoints
- Function to create all database tables
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models (SQLAlchemy 2.0 standard)
class Base(DeclarativeBase):
    pass

# Dependency to get DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)