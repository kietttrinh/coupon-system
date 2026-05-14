"""
CRUD operations for the Coupon Schedule model.

This module contains functions for:
- Creating new coupon schedules
- Retrieving schedules for a specific coupon
- Retrieving active schedules at a given time
- Updating schedule information
- Deleting schedules
- Checking for schedule overlaps (uses overlap processing algorithm)

All functions receive a database session and perform the specified operations.
Note: Overlap validation is performed before creating new schedules.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models.coupon_schedule import CouponSchedule
from app.schemas.coupon_schedule import CouponScheduleCreate, CouponScheduleUpdate


def check_schedule_overlap(
    db: Session, 
    coupon_id: int, 
    start_time: datetime, 
    end_time: datetime, 
    exclude_schedule_id: Optional[int] = None
) -> bool:
    """
    Thuật toán kiểm tra Overlap:
    Hai khoảng thời gian giao nhau khi và chỉ khi: Start1 < End2 VÀ End1 > Start2.
    """
    query = db.query(CouponSchedule).filter(
        CouponSchedule.coupon_id == coupon_id,
        CouponSchedule.start_time < end_time,
        CouponSchedule.end_time > start_time
    )
    
    # Loại trừ chính nó khi đang thực hiện thao tác Update
    if exclude_schedule_id:
        query = query.filter(CouponSchedule.id != exclude_schedule_id)
        
    return query.first() is not None


def get_coupon_schedule(db: Session, schedule_id: int) -> Optional[CouponSchedule]:
    """Retrieve a specific schedule by its ID."""
    return db.query(CouponSchedule).filter(CouponSchedule.id == schedule_id).first()


def get_schedules_by_coupon(db: Session, coupon_id: int) -> List[CouponSchedule]:
    """Retrieve all schedules associated with a specific coupon."""
    return db.query(CouponSchedule).filter(
        CouponSchedule.coupon_id == coupon_id
    ).order_by(CouponSchedule.start_time.asc()).all()


def get_active_schedules_at_time(db: Session, target_time: datetime) -> List[CouponSchedule]:
    """
    Retrieve all schedules that are currently active at the given time.
    """
    return db.query(CouponSchedule).filter(
        CouponSchedule.start_time <= target_time,
        CouponSchedule.end_time >= target_time
    ).all()


def create_coupon_schedule(db: Session, schedule_in: CouponScheduleCreate) -> Optional[CouponSchedule]:
    """
    Create a new coupon schedule.
    Returns None if there is a time overlap with an existing schedule for the same coupon.
    """
    if check_schedule_overlap(db, schedule_in.coupon_id, schedule_in.start_time, schedule_in.end_time):
        return None  # Trả về None để tầng API (Routers) tự động raise HTTP 400 Exception
        
    db_schedule = CouponSchedule(**schedule_in.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def update_coupon_schedule(
    db: Session, 
    db_schedule: CouponSchedule, 
    schedule_update: CouponScheduleUpdate
) -> Optional[CouponSchedule]:
    """
    Update an existing schedule.
    Validates for time overlaps if the time ranges are modified.
    Returns None if an overlap is detected.
    """
    update_data = schedule_update.model_dump(exclude_unset=True)
    
    # Tính toán khoảng thời gian mới (nếu có thay đổi, ngược lại giữ nguyên)
    new_start = update_data.get("start_time", db_schedule.start_time)
    new_end = update_data.get("end_time", db_schedule.end_time)
    
    # Nếu có thay đổi về thời gian, bắt buộc phải kiểm tra overlap lại
    if "start_time" in update_data or "end_time" in update_data:
        if check_schedule_overlap(db, db_schedule.coupon_id, new_start, new_end, exclude_schedule_id=db_schedule.id):
            return None
            
    for field, value in update_data.items():
        setattr(db_schedule, field, value)
        
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def delete_coupon_schedule(db: Session, schedule_id: int) -> bool:
    """Delete a schedule from the database."""
    db_schedule = get_coupon_schedule(db, schedule_id=schedule_id)
    if db_schedule:
        db.delete(db_schedule)
        db.commit()
        return True
    return False