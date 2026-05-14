"""
Core configuration module for the Coupon System.
This module handles loading environment variables and configuring application settings.
"""

import secrets
from pathlib import Path
from typing import Any, List, Optional, Union

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# TỰ ĐỘNG DÒ TÌM ĐƯỜNG DẪN GỐC (ROOT DIRECTORY)
# File này đang ở: coupon-system/backend/app/core/config.py
# .parent lần 1 -> core
# .parent lần 2 -> app
# .parent lần 3 -> backend
# .parent lần 4 -> coupon-system (Thư mục gốc)
CURRENT_FILE_PATH = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE_PATH.parent.parent.parent.parent
BACKEND_DIR = CURRENT_FILE_PATH.parent.parent.parent

class Settings(BaseSettings):
    # App settings
    APP_NAME: str
    ENVIRONMENT: str 
    DEBUG: bool 

    # Server settings
    HOST: str 
    PORT: int 

    # API settings
    API_V1_STR: str 

    # MySQL Database settings
    MYSQL_HOST: str 
    MYSQL_PORT: int 
    MYSQL_USER: str 
    MYSQL_PASSWORD: str 
    MYSQL_DB: str 

    # Database URL
    DATABASE_URL: str = ""

    # # Telegram Bot settings
    # TELEGRAM_BOT_TOKEN: str = ""
    # TELEGRAM_ADMIN_CHAT_ID: Optional[str] = None

    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # CORS settings
    CORS_ORIGINS: Union[List[str], str] = []

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str) and v != "":
            return v
        
        # Tự động build chuỗi kết nối từ các biến MYSQL_* nếu không có DATABASE_URL
        return f"mysql+pymysql://{info.data.get('MYSQL_USER')}:{info.data.get('MYSQL_PASSWORD')}@{info.data.get('MYSQL_HOST')}:{info.data.get('MYSQL_PORT')}/{info.data.get('MYSQL_DB')}"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        # Parse chuỗi "http://localhost:8000,http://127.0.0.1:8000" thành List
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    # Pydantic v2 Config
    model_config = SettingsConfigDict(
        # CUNG CẤP NHIỀU ĐƯỜNG DẪN DỰ PHÒNG: 
        # Pydantic sẽ quét từ trên xuống dưới, thấy .env ở đâu sẽ lấy ở đó
        env_file=(
            str(ROOT_DIR / ".env"),      # Ưu tiên 1: Lấy .env ở gốc coupon-system/
            str(BACKEND_DIR / ".env"),   # Ưu tiên 2: Lấy .env ở backend/
            ".env"                       # Ưu tiên 3: Lấy ở thư mục hiện tại (fallback)
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()