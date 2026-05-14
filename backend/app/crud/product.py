"""
CRUD operations for the Product model.

This module contains functions for:
- Creating new products
- Retrieving products by various criteria (id, name, etc.)
- Updating product information (price, stock, etc.)
- Deleting products
- Checking stock availability
- Managing inventory levels

All functions receive a database session and perform the specified operations.
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Tuple

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Retrieve a product by its ID."""
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_name(db: Session, name: str) -> Optional[Product]:
    """Retrieve a product by its exact name (useful for duplicate checks)."""
    return db.query(Product).filter(Product.name == name).first()


def get_products(db: Session, skip: int = 0, limit: int = 50) -> Tuple[List[Product], int]:
    """Retrieve a list of products with pagination, returning items and total count."""
    total = db.query(Product).count()
    items = db.query(Product).order_by(Product.id.desc()).offset(skip).limit(limit).all()
    return items, total


def create_product(db: Session, product_in: ProductCreate) -> Product:
    """Create a new product in the database."""
    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, db_product: Product, product_update: ProductUpdate) -> Product:
    """
    Update product information.
    Only updates the fields that are explicitly provided in the request.
    """
    update_data = product_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
        
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    """Delete a product from the database."""
    db_product = get_product(db, product_id=product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False


def check_stock_availability(db: Session, product_id: int, quantity: int = 1) -> bool:
    """Check if a product has enough stock available."""
    db_product = get_product(db, product_id=product_id)
    if not db_product:
        return False
    return db_product.stock >= quantity


def reduce_inventory(db: Session, product_id: int, quantity: int = 1) -> Optional[Product]:
    """
    Reduce the inventory level of a product.
    Returns the updated product if successful, or None if insufficient stock.
    """
    db_product = get_product(db, product_id=product_id)
    
    if db_product and db_product.stock >= quantity:
        db_product.stock -= quantity
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
        
    return None