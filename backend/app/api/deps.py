"""
Dependencies for the Coupon System API.

This module contains dependency functions used across API endpoints:
- Database session dependency
- Current user authentication
- Admin permission checks
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.core.database import SessionLocal

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Get current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Trong JWT, 'sub' lưu trữ giá trị subject (ở đây là user_id dạng string)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        token_data = schemas.TokenPayload(sub=user_id_str)
    except (JWTError, ValidationError):
        raise credentials_exception
        
    # Ép kiểu sub về int để query vào database
    try:
        user_id = int(token_data.sub)
    except ValueError:
        raise credentials_exception

    # Sử dụng hàm get_user từ module crud đã được gom nhóm
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise credentials_exception
        
    return user


def get_current_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get current admin user. 
    Verifies that the authenticated user holds the ADMIN role.
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user