"""
User model representing the 'users' table in the database.

This model defines the structure for user accounts in the system:
- id: Primary key
- username: Unique username for login
- password_hash: Hashed password (never store plain text passwords)
- role: User role (ENUM: 'user' or 'admin')
- telegram_chat_id: Telegram chat ID for admin bot authentication (nullable)

Relationships:
- One-to-many with Usage_Logs (a user can have many usage logs)
"""

from sqlalchemy import Column, Integer, String, Enum, BigInteger, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_chat_id = Column(BigInteger, unique=True, index=True, nullable=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False) 
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    create_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship: Một user có thể có nhiều usage logs
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")