"""
Recommend coupons system (Greedy Dynamic Sorting) algorithm.

This module implements the algorithm for recommending coupons to users
by sorting them based on actual discount value in descending order.

Algorithm steps:
1. Input: current price of order/product and list of active coupons.
2. Filter out coupons where min_order_value > current_price.
3. For each remaining coupon, calculate actual discount using the pricing engine.
4. Sort the filtered coupons by actual discount amount in descending order.
5. Return the sorted list (highest discount first).

Time complexity: O(N log N) where N is the number of valid coupons.
Space complexity: O(N) for storing the filtered and sorted list.
"""

from typing import List
from decimal import Decimal

from app.models.coupon import Coupon
from app.schemas.coupon import CouponResponse
from app.algorithms.pricing_engine.discount_calculator import validate_and_calculate_discount

def greedy_dynamic_sorting(valid_coupons: List[Coupon], order_value: Decimal) -> List[CouponResponse]:
    """
    Sorts and recommends the best coupons for a given order value.
    
    Args:
        valid_coupons: List of active, time-valid Coupon SQLAlchemy models.
        order_value: The total value of the user's cart/order.
        
    Returns:
        List of CouponResponse schemas sorted by highest discount amount.
    """
    processed_coupons = []

    for coupon in valid_coupons:
       # Filter
        if coupon.min_order_value and order_value < coupon.min_order_value:
            continue
            
        # Bước 2: Dùng Pricing Engine để tính toán chính xác số tiền được giảm
        # (Lưu ý: Chúng ta không truyền schedule vào đây vì validation thời gian đã được
        # xử lý ở tầng API/CRUD trước khi list valid_coupons được truyền vào hàm này)
        calc_result = validate_and_calculate_discount(
            coupon=coupon, 
            order_value=order_value, 
            schedules=None # Bỏ qua check thời gian vì đã check rồi
        )
        
        # Nếu logic Pricing Engine từ chối (vì lý do nào đó), bỏ qua mã này
        if not calc_result.is_valid:
            continue
            
        # Bước 3: Chuyển đổi Model thành Schema (để trả về Frontend) và đính kèm discount tạm thời để sort
        # Mẹo: Pydantic cho phép tạo object bằng dict thông qua model_validate
        coupon_schema = CouponResponse.model_validate(coupon)
        
        # Lưu vào một tuple: (schema, actual_discount) để dễ sort
        processed_coupons.append((coupon_schema, calc_result.discount_amount))

    # Bước 4: Sort (Tham lam - Lấy cái giảm nhiều tiền nhất)
    # x[1] chính là actual_discount đã lưu trong tuple
    processed_coupons.sort(key=lambda x: x[1], reverse=True)

    # Bước 5: Chỉ lấy ra cái schema (bỏ cái discount tạm đi) để trả về
    return [item[0] for item in processed_coupons]