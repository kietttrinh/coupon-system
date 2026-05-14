"""
Pydantic schemas for User model validation and serialization.

This module defines schemas for:
- UserCreate: Input validation for creating new users
- UserUpdate: Input validation for updating user information
- UserInDB: Representation of user data as stored in database (includes hashed password)
- UserResponse: Output schema for API responses (excludes sensitive fields like password hash)
- Token: Schema for JWT token responses
- TokenPayload: Schema for decoding JWT tokens
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

# ==========================
# TOKEN SCHEMAS
# ==========================
class TokenPayload(BaseModel):
    """Token payload schema for JWT decoding."""
    sub: str # Convention của JWT thường dùng 'sub' (subject) để lưu user_id


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str


# ==========================
# USER SCHEMAS
# ==========================
class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., max_length=255)
    email: EmailStr
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)
    telegram_chat_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=8)
    telegram_chat_id: Optional[int] = None


class UserInDB(UserBase):
    """User schema as stored in database (Includes sensitive data)."""
    id: int
    telegram_chat_id: Optional[int] = None
    password_hash: str
    create_at: datetime
    updated_at: datetime

    # Pydantic V2 syntax để map với SQLAlchemy ORM
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """User schema for API responses (Excludes sensitive fields like password_hash)."""
    id: int
    telegram_chat_id: Optional[int] = None
    create_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)