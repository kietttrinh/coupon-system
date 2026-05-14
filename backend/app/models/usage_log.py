"""
Usage log model representing the 'usage_logs' table in the database.

This model defines the structure for tracking coupon usage:
- id: Primary key
- user_id: Foreign key referencing users.id
- coupon_id: Foreign key referencing coupons.id
- used_at: Timestamp when the coupon was used

Constraints:
- Enforces business rules like "each user can use each coupon only once"
  (handled through unique constraints or validation logic)

Relationships:
- Many-to-one with User (each usage log is associated with one user)
- Many-to-one with Coupon (each usage log is for one coupon)
"""
"""
Usage log model representing the 'usage_logs' table in the database.

This model defines the structure for tracking coupon usage:
- id: Primary key
- user_id: Foreign key referencing users.id
- coupon_id: Foreign key referencing coupons.id
- used_at: Timestamp when the coupon was used

Constraints:
- Enforces business rules like "each user can use each coupon only once"
  (handled through unique constraints or validation logic)

Relationships:
- Many-to-one with User (each usage log is associated with one user)
- Many-to-one with Coupon (each usage log is for one coupon)
"""

from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Bổ sung các trường từ file CSDL gốc để tránh lỗi NOT NULL constraint
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    order_value = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), nullable=False)
    final_price = Column(DECIMAL(10, 2), nullable=False)
    
    used_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    # Ràng buộc cấp CSDL: Đảm bảo một User chỉ dùng một Coupon đúng 1 lần
    __table_args__ = (
        UniqueConstraint('user_id', 'coupon_id', name='uix_user_coupon_usage'),
    )

    # Relationships
    user = relationship("User", back_populates="usage_logs")
    coupon = relationship("Coupon", back_populates="usage_logs")