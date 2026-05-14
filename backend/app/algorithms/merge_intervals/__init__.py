"""
Merge intervals algorithms package.

This package contains algorithms for processing and validating time intervals,
specifically for ensuring coupon schedules do not overlap.
"""

from .overlap_processing import merge_schedules_and_calculate_duration

__all__ = ["merge_schedules_and_calculate_duration"]