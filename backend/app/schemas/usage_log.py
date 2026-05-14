"""
Pydantic schemas for Usage Log model validation and serialization.

This module defines schemas for:
- UsageLogCreate: Input validation for creating new usage logs
- UsageLogInDB: Representation of usage log data as stored in database
- UsageLogResponse: Output schema for API responses
- UsageLogList: Schema for paginated usage log lists
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class UsageLogBase(BaseModel):
    """Base schema for common properties across all Usage Log schemas."""
    user_id: int = Field(..., description="ID of the user who applied the coupon")
    coupon_id: int = Field(..., description="ID of the coupon used")
    product_id: Optional[int] = Field(None, description="ID of the specific product (if applicable)")
    
    # Financial data validation
    order_value: Decimal = Field(..., ge=0, description="Original value of the order/product")
    discount_amount: Decimal = Field(..., ge=0, description="Amount discounted by the coupon")
    final_price: Decimal = Field(..., ge=0, description="Final price paid after discount")


class UsageLogCreate(UsageLogBase):
    """Input validation for creating new usage logs (called during checkout)."""
    pass


class UsageLogInDB(UsageLogBase):
    """Representation of usage log data as stored in database."""
    id: int
    used_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsageLogResponse(UsageLogBase):
    """Output schema for API responses."""
    id: int
    used_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsageLogList(BaseModel):
    """Schema for paginated usage log lists."""
    items: List[UsageLogResponse]
    total: int = Field(..., description="Total number of records matching the query")
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=100)