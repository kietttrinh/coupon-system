"""
Pricing engine algorithm for discount calculation.

This module implements the centralized logic for calculating discount amounts
based on coupon type, value, and constraints.

Calculation logic:
1. Check if current price meets minimum order value requirement
   - If not, return 0 discount (coupon not applicable)
2. For FIXED coupons: discount_amount = discount_value
3. For PERCENT coupons:
   - discount_amount = current_price * (discount_value / 100)
   - Apply maximum discount cap if max_discount_amount is set
4. Ensure final price doesn't go negative:
   - Return min(discount_amount, current_price)

This algorithm is used in:
- Coupon validation endpoint to calculate final price
- Recommend coupons system to determine actual discount value
- Anywhere discount calculation is needed in the system

The algorithm is designed to be pure and testable, taking a coupon dictionary
and current price as inputs and returning the discount amount.
"""

from decimal import Decimal
from typing import Optional, List
from datetime import datetime

from app.models.coupon import Coupon, DiscountTypeEnum
from app.models.coupon_schedule import CouponSchedule
from app.schemas.coupon import CouponValidationResult


def validate_and_calculate_discount(
    coupon: Coupon, 
    order_value: Decimal, 
    schedules: Optional[List[CouponSchedule]] = None
) -> CouponValidationResult:
    """
    Core pricing engine that validates and calculates the final discount.
    Pure and testable function.
    """
    order_value = Decimal(str(order_value))
    
    # 0. Basic Validation (Active status & Time)
    if not coupon.is_active:
        return CouponValidationResult(
            is_valid=False, error_message="Coupon is currently inactive."
        )

    if schedules is not None and len(schedules) > 0:
        current_time = datetime.now()
        is_time_valid = any(
            sched.start_time <= current_time <= sched.end_time for sched in schedules
        )
        if not is_time_valid:
            return CouponValidationResult(
                is_valid=False, error_message="Coupon is not valid at this time."
            )

    # 1. Check minimum order value requirement
    if coupon.min_order_value and order_value < coupon.min_order_value:
        return CouponValidationResult(
            is_valid=False, 
            error_message=f"Minimum order value of {coupon.min_order_value} required."
        )

    # 2 & 3. Calculate discount amount based on type
    discount_amount = Decimal('0.00')

    if coupon.discount_type == DiscountTypeEnum.FIXED:
        discount_amount = coupon.discount_value
        
    elif coupon.discount_type == DiscountTypeEnum.PERCENT:
        # Tính toán phần trăm (VD: 20% = 20 / 100)
        calculated_discount = order_value * (coupon.discount_value / Decimal('100.0'))
        
        # Apply maximum discount cap if max_discount_amount is set
        if coupon.max_discount_amount:
            discount_amount = min(calculated_discount, coupon.max_discount_amount)
        else:
            discount_amount = calculated_discount

    # 4. Ensure final price doesn't go negative (Return min(discount_amount, current_price))
    discount_amount = min(discount_amount, order_value)
    final_price = order_value - discount_amount

    # Trả về Result Schema chuẩn
    return CouponValidationResult(
        is_valid=True,
        coupon_id=coupon.id,
        code=coupon.code,
        discount_amount=discount_amount,
        final_price=final_price,
        discount_type=coupon.discount_type,
        discount_value=coupon.discount_value
    )