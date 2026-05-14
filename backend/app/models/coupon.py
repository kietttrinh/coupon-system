"""
Coupon model representing the 'coupons' table in the database.

This model defines the structure for coupons/discount codes:
- id: Primary key
- code: Unique coupon code (string)
- visibility: Coupon visibility (ENUM: 'PUBLIC' or 'PRIVATE')
- discount_type: Type of discount (ENUM: 'FIXED' or 'PERCENT')
- discount_value: Value of the discount (amount or percentage)
- max_discount_amount: Maximum discount amount for PERCENT type (nullable)
- min_order_value: Minimum order value required to use coupon (nullable)

Relationships:
- One-to-many with Coupon_Schedules (a coupon can have multiple time schedules)
- One-to-many with Usage_Logs (a coupon can be used many times by different users)
"""

from sqlalchemy import Column, Integer, String, Boolean, Enum, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class VisibilityEnum(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class DiscountTypeEnum(str, enum.Enum):
    FIXED = "FIXED"
    PERCENT = "PERCENT"


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(255), unique=True, index=True, nullable=False)
    visibility = Column(Enum(VisibilityEnum), default=VisibilityEnum.PRIVATE, index=True, nullable=False)
    discount_type = Column(Enum(DiscountTypeEnum), nullable=False)
    discount_value = Column(DECIMAL(10, 2), nullable=False)
    max_discount_amount = Column(DECIMAL(10, 2), nullable=True)
    min_order_value = Column(DECIMAL(10, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit timestamps
    create_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    # Sử dụng string name để tránh circular imports giữa các models
    schedules = relationship("CouponSchedule", back_populates="coupon", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="coupon", cascade="all, delete-orphan")