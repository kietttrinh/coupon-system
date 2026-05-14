"""
Overlap processing algorithm for coupon schedule validation.

This module implements the merge intervals algorithm to ensure
that no two time schedules for the same coupon overlap.

Algorithm steps:
1. Retrieve all existing schedules for a given coupon from the database
2. Add the new schedule to be validated
3. Sort all schedules by start time
4. Linearly iterate through sorted schedules to check for overlaps
5. If any overlap is found (current start <= previous end), reject the new schedule

Time complexity: O(N log N) for sorting + O(N) for linear scan = O(N log N)
Space complexity: O(N) for storing the schedule list

This algorithm is triggered when an admin adds a new time schedule
via the Telegram bot `/add_time` command.
"""

"""
Merge Intervals algorithm for Coupon Schedules.

This module implements the classic Merge Intervals algorithm to calculate
the true, non-overlapping total active time of a coupon.

Algorithm steps (Merge Intervals):
1. Input: List of CouponSchedule objects.
2. Sort all schedules by their start_time.
3. Initialize a 'merged' list.
4. Iterate through sorted schedules:
   - If 'merged' is empty or current start_time > last merged end_time:
     -> No overlap, add to 'merged'.
   - Else if current start_time <= last merged end_time (Overlap exists):
     -> Update the end_time of the last merged interval to be the max(last_end, current_end).
5. Calculate total duration from the 'merged' list.

Time complexity: O(N log N)
Space complexity: O(N)
"""

from typing import List
from datetime import timedelta

from app.models.coupon_schedule import CouponSchedule


def merge_schedules_and_calculate_duration(schedules: List[CouponSchedule]) -> timedelta:
    """
    Takes a list of schedules, merges any overlapping times, 
    and returns the total exact duration the coupon is active.
    
    Args:
        schedules: A list of CouponSchedule objects from the database.
        
    Returns:
        A datetime.timedelta object representing the total active time.
    """
    if not schedules:
        return timedelta(0)

    # Bước 1: Sort lịch trình theo thời gian bắt đầu
    sorted_schedules = sorted(schedules, key=lambda x: x.start_time)
    
    # Bước 2: Khởi tạo mảng merged với phần tử đầu tiên
    merged = [
        {"start": sorted_schedules[0].start_time, "end": sorted_schedules[0].end_time}
    ]

    # Bước 3: Thuật toán Merge Intervals cốt lõi
    for current in sorted_schedules[1:]:
        last_merged = merged[-1]

        # Kiểm tra Overlap: Nếu thời gian bắt đầu của hiện tại <= kết thúc của cái trước đó
        if current.start_time <= last_merged["end"]:
            # Gộp lại: Cập nhật thời gian kết thúc bằng giá trị lớn hơn
            last_merged["end"] = max(last_merged["end"], current.end_time)
        else:
            # Không overlap: Thêm một khoảng thời gian mới độc lập
            merged.append({"start": current.start_time, "end": current.end_time})

    # Bước 4: Tính tổng thời gian từ các khoảng đã được gộp (không còn overlap)
    total_duration = timedelta(0)
    for interval in merged:
        total_duration += (interval["end"] - interval["start"])

    return total_duration