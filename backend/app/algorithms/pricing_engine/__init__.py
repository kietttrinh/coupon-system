"""
Pricing engine algorithms package.

This package contains algorithms for calculating discount amounts
based on coupon properties and current order price.
"""

from .discount_calculator import validate_and_calculate_discount

__all__ = ["validate_and_calculate_discount"]