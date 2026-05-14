"""
Authentication-related API endpoints for the Coupon System.

This module defines endpoints for user authentication and authorization:
- POST /api/v1/auth/register - Register a new user
- POST /api/v1/auth/login - Login user and return access token
- POST /api/v1/auth/logout - Logout user (client-side implementation)
- GET /api/v1/auth/me - Get current user profile information
- POST /api/v1/auth/refresh - Refresh access token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app import crud, schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate
) -> Any:
    """
    Create new user.
    """
    # Kiểm tra xem email hoặc username đã tồn tại chưa
    user_by_email = crud.get_user_by_email(db, email=user_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
        
    user_by_username = crud.get_user_by_username(db, username=user_in.username)
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
        
    user = crud.create_user(db, user=user_in)
    return user


@router.post("/login", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Note: form_data.username can be mapped to either email or username depending on your preference.
    Here we map it to username to match our CRUD logic.
    """
    user = crud.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Trong JWT, field subject (sub) phải là string
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout_user() -> Any:
    """
    Logout user (client-side token removal).
    Note: With JWT, true logout requires a token blacklist or client-side removal.
    """
    return {"msg": "Successfully logged out. Please remove token on client side."}


@router.get("/me", response_model=schemas.UserResponse)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user profile information.
    """
    return current_user


@router.post("/refresh", response_model=schemas.Token)
def refresh_access_token(
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Refresh access token for the currently authenticated user.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(current_user.id), expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }