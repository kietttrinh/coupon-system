"""
Product model representing the 'products' table in the database.

This model defines the structure for products in the inventory:
- id: Primary key
- name: Product name
- base_price: Base price of the product (DECIMAL)
- stock: Current inventory quantity (INT)

Relationships:
- No direct relationships to other tables (products are referenced indirectly through usage)
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, default=0, nullable=False)

    description = Column(String(1000), nullable=True)

    # Audit timestamps
    create_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())