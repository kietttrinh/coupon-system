"""
Coupon schedule model representing the 'coupon_schedules' table in the database.

This model defines the structure for coupon time schedules:
- id: Primary key
- coupon_id: Foreign key referencing coupons.id
- start_time: Start timestamp when coupon becomes active
- end_time: End timestamp when coupon expires

Constraints:
- Ensures no overlapping schedules for the same coupon (validated by overlap processing algorithm)
- start_time must be before end_time

Relationships:
- Many-to-one with Coupon (each schedule belongs to one coupon)
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class CouponSchedule(Base):
    __tablename__ = "coupon_schedules"

    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Audit timestamps
    create_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    # Sử dụng string "Coupon" để tham chiếu ngược lại tránh circular import
    coupon = relationship("Coupon", back_populates="schedules")