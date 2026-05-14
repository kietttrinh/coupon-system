"""
Pydantic schemas for Coupon Schedule model validation and serialization.

This module defines schemas for:
- CouponScheduleCreate: Input validation for creating new coupon schedules
- CouponScheduleUpdate: Input validation for updating coupon schedule information
- CouponScheduleInDB: Representation of coupon schedule data as stored in database
- CouponScheduleResponse: Output schema for API responses
"""

"""
Pydantic schemas for Coupon Schedule model validation and serialization.

This module defines schemas for:
- CouponScheduleCreate: Input validation for creating new coupon schedules
- CouponScheduleUpdate: Input validation for updating coupon schedule information
- CouponScheduleInDB: Representation of coupon schedule data as stored in database
- CouponScheduleResponse: Output schema for API responses
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from datetime import datetime

class CouponScheduleBase(BaseModel):
    """Base schema with common coupon schedule attributes."""
    start_time: datetime = Field(..., description="Start timestamp when coupon becomes active")
    end_time: datetime = Field(..., description="End timestamp when coupon expires")

    @model_validator(mode='after')
    def validate_time_range(self) -> 'CouponScheduleBase':
        """Ensure start_time is strictly before end_time."""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError('start_time must be strictly before end_time')
        return self


class CouponScheduleCreate(CouponScheduleBase):
    """Input validation for creating new coupon schedules."""
    coupon_id: int = Field(..., description="ID of the coupon this schedule belongs to")


class CouponScheduleUpdate(BaseModel):
    """Input validation for updating coupon schedule information."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_time_range(self) -> 'CouponScheduleUpdate':
        """Ensure start_time is strictly before end_time if both are updated together."""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError('start_time must be strictly before end_time')
        return self


class CouponScheduleInDB(CouponScheduleBase):
    """Representation of coupon schedule data as stored in database."""
    id: int
    coupon_id: int
    create_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CouponScheduleResponse(CouponScheduleBase):
    """Output schema for API responses."""
    id: int
    coupon_id: int
    create_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)