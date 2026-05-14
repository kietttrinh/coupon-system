"""
Pydantic schemas for Coupon model validation and serialization.

This module defines schemas for:
- CouponCreate: Input validation for creating new coupons
- CouponUpdate: Input validation for updating coupon information
- CouponInDB: Representation of coupon data as stored in database
- CouponResponse: Output schema for API responses
- CouponList: Schema for paginated coupon lists
- CouponValidate: Schema for coupon validation requests (includes price for discount calculation)
- CouponValidateResponse: Schema for coupon validation responses (includes discount amount and final price)
- CouponValidationResult: Schema for coupon validation results
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class DiscountType(str, Enum):
    FIXED = "FIXED"
    PERCENT = "PERCENT"


class Visibility(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class CouponBase(BaseModel):
    """Base coupon schema with common fields."""
    code: str = Field(..., max_length=255)
    visibility: Visibility = Visibility.PRIVATE
    discount_type: DiscountType
    discount_value: float = Field(..., gt=0)
    max_discount_amount: Optional[float] = Field(None, gt=0)
    min_order_value: Optional[float] = Field(None, gt=0)
    is_active: bool = True


class CouponCreate(CouponBase):
    """Schema for creating a new coupon."""
    pass


class CouponUpdate(BaseModel):
    """Schema for updating coupon information."""
    code: Optional[str] = Field(None, max_length=255)
    visibility: Optional[Visibility] = None
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = Field(None, gt=0)
    max_discount_amount: Optional[float] = Field(None, gt=0)
    min_order_value: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None

class CouponInDB(CouponBase):
    """Coupon schema as stored in database."""
    id: int
    create_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CouponResponse(CouponBase):
    """Coupon schema for API responses."""
    id: int
    create_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CouponValidate(BaseModel):
    """Schema for coupon validation requests."""
    code: str = Field(..., max_length=255)
    order_value: float = Field(..., gt=0)


class CouponValidationResult(BaseModel):
    """Schema for coupon validation results."""
    is_valid: bool
    coupon_id: Optional[int] = None
    code: Optional[str] = None
    discount_amount: float = 0.0
    final_price: float = 0.0
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)