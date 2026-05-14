"""
SQLAlchemy models package for the Coupon System.

This package contains all database model definitions representing tables in the MySQL database.
"""

from app.core.database import Base

from app.models.user import User, UserRole
from app.models.product import Product
from app.models.coupon import Coupon, VisibilityEnum, DiscountTypeEnum
from app.models.coupon_schedule import CouponSchedule
from app.models.usage_log import UsageLog

# Dùng __all__ để định nghĩa rõ ràng những class nào sẽ được export 
# khi module khác gọi: `from app.models import *`
__all__ = [
    "User",
    "UserRole",
    "Product",
    "Coupon",
    "VisibilityEnum",
    "DiscountTypeEnum",
    "CouponSchedule",
    "UsageLog",
]