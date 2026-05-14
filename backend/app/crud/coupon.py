"""
CRUD operations for the Coupon model.

This module contains functions for:
- Creating new coupons
- Retrieving coupons by various criteria (id, code, visibility, etc.)
- Updating coupon information
- Deactivating/deleting coupons
- Checking coupon validity based on time schedules
- Managing coupon visibility (PUBLIC/PRIVATE)

All functions receive a database session and perform the specified operations.
Note: Time schedule validation is handled separately in the algorithms module.
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Tuple

from app.models.coupon import Coupon, VisibilityEnum
from app.schemas.coupon import CouponCreate, CouponUpdate


def get_coupon(db: Session, coupon_id: int) -> Optional[Coupon]:
    """Retrieve a coupon by its ID."""
    return db.query(Coupon).filter(Coupon.id == coupon_id).first()


def get_coupon_by_code(db: Session, code: str) -> Optional[Coupon]:
    """Retrieve a coupon by its unique code (Case-sensitive based on DB collation)."""
    return db.query(Coupon).filter(Coupon.code == code).first()


def get_coupons(db: Session, skip: int = 0, limit: int = 50) -> Tuple[List[Coupon], int]:
    """Retrieve a list of coupons with pagination, returning items and total count."""
    total = db.query(Coupon).count()
    items = db.query(Coupon).order_by(Coupon.id.desc()).offset(skip).limit(limit).all()
    return items, total


def get_public_coupons(db: Session, active_only: bool = True, private_view: bool = False) -> List[Coupon]:
    """
    Retrieve all PUBLIC coupons.
    Used for displaying available coupons to users or feeding the recommendation engine.
    """
    query = db.query(Coupon).filter(Coupon.visibility == VisibilityEnum.PUBLIC)
    
    if private_view: 
        query = db.query(Coupon)

    if active_only:
        query = query.filter(Coupon.is_active == True)
    return query.all()


def create_coupon(db: Session, coupon_in: CouponCreate) -> Coupon:
    """Create a new coupon in the database."""
    db_coupon = Coupon(**coupon_in.model_dump())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


def update_coupon(db: Session, db_coupon: Coupon, coupon_update: CouponUpdate) -> Coupon:
    """
    Update coupon information.
    Only updates the fields that are explicitly provided in the request.
    """
    update_data = coupon_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_coupon, field, value)
        
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


def deactivate_coupon(db: Session, coupon_id: int) -> Optional[Coupon]:
    """Soft-delete a coupon by setting is_active to False."""
    db_coupon = get_coupon(db, coupon_id=coupon_id)
    if db_coupon:
        db_coupon.is_active = False
        db.commit()
        db.refresh(db_coupon)
        return db_coupon
    return None


def delete_coupon(db: Session, coupon_id: int) -> bool:
    """
    Hard-delete a coupon from the database.
    WARNING: This will cascade and delete all associated UsageLogs and Schedules.
    """
    db_coupon = get_coupon(db, coupon_id=coupon_id)
    if db_coupon:
        db.delete(db_coupon)
        db.commit()
        return True
    return False