"""
Security utilities for the Coupon System.

This module handles:
- Password hashing and verification using bcrypt
- JWT token creation and validation
"""

from datetime import datetime, timedelta, timezone
from typing import Union, Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate password hash from plain password.
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[int, str], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    """
    # Sử dụng timezone.utc thay vì utcnow() đã bị deprecated trong Python 3.12+
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt