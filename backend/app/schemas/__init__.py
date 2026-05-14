"""
Pydantic schemas package for the Coupon System.

This package contains all data validation and serialization models
used for API request and response bodies.
"""

# User schemas
from app.schemas.user import (
    UserBase, 
    UserCreate, 
    UserUpdate, 
    UserInDB, 
    UserResponse,
    Token,
    TokenPayload
)

# Product schemas
from app.schemas.product import (
    ProductBase, 
    ProductCreate, 
    ProductUpdate, 
    ProductInDB, 
    ProductResponse, 
    ProductList
)

# Coupon Schedule schemas
from app.schemas.coupon_schedule import (
    CouponScheduleBase, 
    CouponScheduleCreate, 
    CouponScheduleUpdate,
    CouponScheduleInDB, 
    CouponScheduleResponse
)

# Coupon schemas
from app.schemas.coupon import (
    CouponBase, 
    CouponCreate, 
    CouponUpdate, 
    CouponInDB, 
    CouponResponse,
    CouponValidate, 
    CouponValidationResult
)

# Usage Log schemas
from app.schemas.usage_log import (
    UsageLogBase, 
    UsageLogCreate, 
    UsageLogInDB, 
    UsageLogResponse, 
    UsageLogList
)

# Khai báo __all__ để kiểm soát những gì được export khi dùng import *
__all__ = [
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserInDB", "UserResponse", "Token", "TokenPayload",
    
    # Product
    "ProductBase", "ProductCreate", "ProductUpdate", "ProductInDB", "ProductResponse", "ProductList",
    
    # Coupon Schedule
    "CouponScheduleBase", "CouponScheduleCreate", "CouponScheduleUpdate", "CouponScheduleInDB", "CouponScheduleResponse",
    
    # Coupon
    "CouponBase", "CouponCreate", "CouponUpdate", "CouponInDB", "CouponResponse", "CouponValidate", "CouponValidationResult",
    
    # Usage Log
    "UsageLogBase", "UsageLogCreate", "UsageLogInDB", "UsageLogResponse", "UsageLogList"
]

