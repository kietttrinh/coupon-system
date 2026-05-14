"""
API router for version 1 of the Coupon System API.

This module includes all API routers for different resources:
- Authentication endpoints
- Coupon endpoints
- Product endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, coupons, products

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(coupons.router, prefix="/coupons", tags=["coupons"])
api_router.include_router(products.router, prefix="/products", tags=["products"])