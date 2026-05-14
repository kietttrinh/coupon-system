"""
CRUD operations package for the Coupon System.

This package contains all database interaction functions
separated by model/entity type.
"""

# Import User CRUD operations
from app.crud.user import (
    get_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_telegram_id,
    get_users,
    create_user,
    update_user,
    delete_user,
    authenticate_user
)

# Import Product CRUD operations
from app.crud.product import (
    get_product,
    get_product_by_name,
    get_products,
    create_product,
    update_product,
    delete_product,
    check_stock_availability,
    reduce_inventory
)

# Import Coupon CRUD operations
from app.crud.coupon import (
    get_coupon,
    get_coupon_by_code,
    get_coupons,
    get_public_coupons,
    create_coupon,
    update_coupon,
    deactivate_coupon,
    delete_coupon
)

# Import Coupon Schedule CRUD operations
from app.crud.coupon_schedule import (
    check_schedule_overlap,
    get_coupon_schedule,
    get_schedules_by_coupon,
    get_active_schedules_at_time,
    create_coupon_schedule,
    update_coupon_schedule,
    delete_coupon_schedule
)

# Import Usage Log CRUD operations
from app.crud.usage_log import (
    check_user_coupon_usage,
    create_usage_log,
    get_usage_logs,
    get_coupon_usage_stats,
    get_user_usage_stats,
    delete_usage_log
)