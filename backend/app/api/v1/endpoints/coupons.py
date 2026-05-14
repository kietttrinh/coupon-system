"""
Coupon-related API endpoints for the Coupon System.

This module defines all RESTful endpoints related to coupon operations:
- GET /api/v1/coupons - Retrieve list of public coupons
- GET /api/v1/coupons/recommend - Recommend best coupons based on order value
- GET /api/v1/coupons/{coupon_id} - Retrieve specific coupon details
- POST /api/v1/coupons/validate - Validate a coupon code for application
- POST /api/v1/coupons - Create new coupon (admin only)
- PUT /api/v1/coupons/{coupon_id} - Update existing coupon (admin only)
- DELETE /api/v1/coupons/{coupon_id} - Delete coupon (admin only)
"""

from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
# Import our core business logic algorithms
from app.algorithms.pricing_engine import validate_and_calculate_discount
from app.algorithms.greedy_sorting import greedy_dynamic_sorting

router = APIRouter()


@router.get("/", response_model=List[schemas.CouponResponse])
def read_coupons(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve list of public coupons.
    """
    coupons = crud.get_public_coupons(db, active_only=False, private_view=True)
    # Apply pagination manually here since get_public_coupons might not have it
    return coupons[skip : skip + limit]


@router.get("/recommend", response_model=List[schemas.CouponResponse])
def recommend_coupons(
    *,
    db: Session = Depends(deps.get_db),
    order_value: float = Query(..., gt=0, description="Order value to calculate best discounts"),
    limit: int = 5,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Greedy Dynamic Sorting: Suggest the best active public coupons 
    based on the specific order value.
    """
    active_public_coupons = crud.get_public_coupons(db, active_only=True)
    
    # Filter coupons that are currently within their active schedule
    current_time = datetime.now()
    valid_coupons = []
    
    for coupon in active_public_coupons:
        schedules = crud.get_schedules_by_coupon(db, coupon.id)
        # Check if current time falls in any of the schedules
        is_time_valid = False
        if not schedules: # If no schedule, assume it's always valid if is_active=True
            is_time_valid = True
        else:
            for sched in schedules:
                if sched.start_time <= current_time <= sched.end_time:
                    is_time_valid = True
                    break
                    
        if is_time_valid:
            valid_coupons.append(coupon)

    # Apply Greedy Sorting Algorithm
    sorted_coupons = greedy_dynamic_sorting(valid_coupons, order_value)
    
    return sorted_coupons[:limit]


@router.get("/{coupon_id}", response_model=schemas.CouponResponse)
def read_coupon(
    *,
    db: Session = Depends(deps.get_db),
    coupon_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get coupon by ID.
    """
    coupon = crud.get_coupon(db=db, coupon_id=coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    return coupon


@router.post("/validate", response_model=schemas.CouponValidationResult)
def validate_coupon_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    coupon_in: schemas.CouponValidate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Validate a coupon code for application during checkout.
    Uses the Pricing Engine for complex calculations.
    """
    coupon = crud.get_coupon_by_code(db, code=coupon_in.code)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid coupon code"
        )

    # Retrieve schedules to check time validity
    schedules = crud.get_schedules_by_coupon(db, coupon.id)

    # Use the separated Pricing Engine algorithm
    result = validate_and_calculate_discount(
        coupon=coupon,
        order_value=coupon_in.order_value,
        schedules=schedules
    )

    if not result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error_message
        )

    # Optional: Log the validation intent or usage here if needed
    
    return result


@router.post("/", response_model=schemas.CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    *,
    db: Session = Depends(deps.get_db),
    coupon_in: schemas.CouponCreate,
    current_user: models.User = Depends(deps.get_current_admin), # Admin only
) -> Any:
    """
    Create new coupon (Admin only).
    """
    coupon = crud.get_coupon_by_code(db, code=coupon_in.code)
    if coupon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A coupon with this code already exists."
        )
    coupon = crud.create_coupon(db, coupon_in=coupon_in)
    return coupon


@router.put("/{coupon_id}", response_model=schemas.CouponResponse)
def update_coupon(
    *,
    db: Session = Depends(deps.get_db),
    coupon_id: int,
    coupon_in: schemas.CouponUpdate,
    current_user: models.User = Depends(deps.get_current_admin), # Admin only
) -> Any:
    """
    Update a coupon (Admin only).
    """
    db_coupon = crud.get_coupon(db=db, coupon_id=coupon_id)
    if not db_coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    # If code is being updated, check for uniqueness
    if coupon_in.code and coupon_in.code != db_coupon.code:
        existing_coupon = crud.get_coupon_by_code(db, code=coupon_in.code)
        if existing_coupon:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A coupon with this code already exists."
            )
            
    updated_coupon = crud.update_coupon(db, db_coupon=db_coupon, coupon_update=coupon_in)
    return updated_coupon


@router.delete("/{coupon_id}")
def delete_coupon(
    *,
    db: Session = Depends(deps.get_db),
    coupon_id: int,
    current_user: models.User = Depends(deps.get_current_admin), # Admin only
) -> Any:
    """
    Delete a coupon (Admin only).
    """
    coupon = crud.get_coupon(db=db, coupon_id=coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    success = crud.delete_coupon(db, coupon_id=coupon_id)
    if not success:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete coupon"
        )
        
    return {"message": "Coupon deleted successfully"}