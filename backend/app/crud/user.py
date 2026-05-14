"""
CRUD operations for the User model.

This module contains functions for:
- Creating new users
- Retrieving users by various criteria (id, username, etc.)
- Updating user information
- Deactivating/deleting users
- Checking password validity
- Managing user roles and Telegram authentication

All functions receive a database session and perform the specified operations.
"""

from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Retrieve a user by their username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by their email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_telegram_id(db: Session, telegram_chat_id: int) -> Optional[User]:
    """Retrieve a user by their Telegram Chat ID for bot authentication."""
    return db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Retrieve a list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user with a hashed password."""
    hashed_password = get_password_hash(user.password)
    
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        telegram_chat_id=user.telegram_chat_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    """
    Update user information. 
    Only updates fields that are explicitly provided in the request.
    Automatically handles password hashing if a new password is provided.
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["password_hash"] = hashed_password
        
    for field, value in update_data.items():
        setattr(db_user, field, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user from the database."""
    db_user = get_user(db, user_id=user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Check password validity and return the user object if authenticated.
    """
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(plain_password=password, hashed_password=user.password_hash):
        return None
    return user