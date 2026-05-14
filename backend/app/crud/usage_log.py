"""
CRUD operations for the Usage Log model.

This module contains functions for:
- Creating new usage log entries (when a coupon is used)
- Retrieving usage logs by various criteria (user, coupon, date range)
- Checking if a user has already used a specific coupon
- Getting usage statistics for coupons or users
- Deleting usage logs (if needed for admin purposes)

All functions receive a database session and perform the specified operations.
Note: Usage limits (like once per user per coupon) are enforced here.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

from app.models.usage_log import UsageLog
from app.schemas.usage_log import UsageLogCreate


def check_user_coupon_usage(db: Session, user_id: int, coupon_id: int) -> bool:
    """Check if a user has already used a specific coupon."""
    exists = db.query(UsageLog).filter(
        UsageLog.user_id == user_id,
        UsageLog.coupon_id == coupon_id
    ).first()
    return exists is not None


def create_usage_log(db: Session, log_in: UsageLogCreate) -> Optional[UsageLog]:
    """
    Create a new usage log entry.
    Enforces the 'once per user per coupon' rule before inserting.
    """
    if check_user_coupon_usage(db, user_id=log_in.user_id, coupon_id=log_in.coupon_id):
        # Trả về None nếu user đã dùng mã này rồi, API layer sẽ handle lỗi này
        return None

    db_log = UsageLog(**log_in.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_usage_logs(
    db: Session,
    user_id: Optional[int] = None,
    coupon_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[UsageLog], int]:
    """Retrieve usage logs with optional filtering and pagination."""
    query = db.query(UsageLog)

    if user_id is not None:
        query = query.filter(UsageLog.user_id == user_id)
    if coupon_id is not None:
        query = query.filter(UsageLog.coupon_id == coupon_id)
    if start_date is not None:
        query = query.filter(UsageLog.used_at >= start_date)
    if end_date is not None:
        query = query.filter(UsageLog.used_at <= end_date)

    total = query.count()
    items = query.order_by(UsageLog.used_at.desc()).offset(skip).limit(limit).all()
    
    return items, total


def get_coupon_usage_stats(db: Session, coupon_id: int) -> Dict[str, Any]:
    """Get statistics for a specific coupon."""
    stats = db.query(
        func.count(UsageLog.id).label('total_uses'),
        func.sum(UsageLog.discount_amount).label('total_discount_given'),
        func.sum(UsageLog.order_value).label('total_revenue_generated')
    ).filter(UsageLog.coupon_id == coupon_id).first()

    return {
        "total_uses": stats.total_uses or 0,
        "total_discount_given": stats.total_discount_given or 0.0,
        "total_revenue_generated": stats.total_revenue_generated or 0.0
    }


def get_user_usage_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Get statistics for a specific user's coupon usage."""
    stats = db.query(
        func.count(UsageLog.id).label('total_coupons_used'),
        func.sum(UsageLog.discount_amount).label('total_money_saved')
    ).filter(UsageLog.user_id == user_id).first()

    return {
        "total_coupons_used": stats.total_coupons_used or 0,
        "total_money_saved": stats.total_money_saved or 0.0
    }


def delete_usage_log(db: Session, log_id: int) -> bool:
    """Delete a usage log (Admin purposes)."""
    db_log = db.query(UsageLog).filter(UsageLog.id == log_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
        return True
    return False