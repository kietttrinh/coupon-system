"""
Product-related API endpoints for the Coupon System.

This module defines all RESTful endpoints related to product operations:
- GET /api/v1/products - Retrieve list of all products (with pagination)
- GET /api/v1/products/{product_id} - Retrieve specific product details
- POST /api/v1/products - Create new product (admin only)
- PUT /api/v1/products/{product_id} - Update existing product (admin only)
- DELETE /api/v1/products/{product_id} - Delete product (admin only)
- GET /api/v1/products/{product_id}/stock - Check product stock availability
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.ProductList)
def read_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve products with pagination.
    """
    items, total = crud.get_products(db, skip=skip, limit=limit)
    return schemas.ProductList(
        items=items,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        size=limit
    )


@router.get("/{product_id}", response_model=schemas.ProductResponse)
def read_product(
    *,
    db: Session = Depends(deps.get_db),
    product_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get product by ID.
    """
    product = crud.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    product_in: schemas.ProductCreate,
    current_user: models.User = Depends(deps.get_current_admin),
) -> Any:
    """
    Create new product (Admin only).
    """
    # Check if a product with the exact same name already exists
    existing_product = crud.get_product_by_name(db, name=product_in.name)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists."
        )
        
    product = crud.create_product(db, product_in=product_in)
    return product


@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    *,
    db: Session = Depends(deps.get_db),
    product_id: int,
    product_in: schemas.ProductUpdate,
    current_user: models.User = Depends(deps.get_current_admin),
) -> Any:
    """
    Update a product (Admin only).
    """
    product = crud.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    product = crud.update_product(db, db_product=product, product_update=product_in)
    return product


@router.delete("/{product_id}")
def delete_product(
    *,
    db: Session = Depends(deps.get_db),
    product_id: int,
    current_user: models.User = Depends(deps.get_current_admin),
) -> Any:
    """
    Delete a product (Admin only).
    """
    product = crud.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    crud.delete_product(db, product_id=product_id)
    return {"message": "Product deleted successfully"}


@router.get("/{product_id}/stock")
def check_product_stock(
    *,
    db: Session = Depends(deps.get_db),
    product_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Check product stock availability.
    """
    product = crud.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return {
        "id": product.id,
        "name": product.name,
        "stock": product.stock,
        "available": product.stock > 0
    }