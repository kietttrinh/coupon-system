"""
Pydantic schemas for Product model validation and serialization.

This module defines schemas for:
- ProductCreate: Input validation for creating new products
- ProductUpdate: Input validation for updating product information
- ProductInDB: Representation of product data as stored in database
- ProductResponse: Output schema for API responses
- ProductList: Schema for paginated product lists
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    """Base schema with common product attributes."""
    name: str = Field(..., max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    
    # Sử dụng Decimal và ge=0 để tránh sai số phẩy động và chặn giá trị âm
    price: Decimal = Field(..., ge=0, decimal_places=2, description="Base price of the product")
    stock: int = Field(default=0, ge=0, description="Current inventory quantity")


class ProductCreate(ProductBase):
    """Input validation for creating new products."""
    pass


class ProductUpdate(BaseModel):
    """Input validation for updating product information (All fields are optional)."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    stock: Optional[int] = Field(None, ge=0)


class ProductInDB(ProductBase):
    """Representation of product data as stored in database."""
    id: int
    create_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    """Output schema for API responses."""
    id: int
    create_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    """Schema for paginated product lists."""
    items: List[ProductResponse]
    total: int = Field(..., description="Total number of products matching the query")
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=100)