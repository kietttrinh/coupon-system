"""
Main FastAPI application entry point for the Coupon System.

This file initializes the FastAPI application, configures middleware (like CORS),
and includes all API routers from different modules.
It serves as the starting point of the backend application.
"""

"""
Main application entry point for the Coupon System API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import engine
# Import Base để SQLAlchemy tự động tạo bảng nếu chưa có
from app.models import Base 

# THÊM DÒNG NÀY ĐỂ XÓA DB CŨ (Chỉ dùng khi dev)
# Base.metadata.drop_all(bind=engine)

# Tạo các bảng trong Database (Chỉ nên dùng cho môi trường dev)
# Ở môi trường production, bạn nên dùng Alembic để quản lý migration
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Coupon System API",
    description="Backend API for managing products, coupons, and usage logs.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Cấu hình CORS (Cross-Origin Resource Sharing)
# Cho phép Frontend hoặc Bot từ các domain khác gọi vào API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lưu ý: Trên Production nên đổi thành list domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn toàn bộ API Router v1 vào ứng dụng chính
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "Welcome to the Coupon System API!",
        "docs": "Visit /docs to explore the API endpoints."
    }