from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# File này đang ở: coupon-system/telegram_bot/config.py
# .parent lần 1 -> telegram_bot/
# .parent lần 2 -> coupon-system/ (Thư mục gốc)
CURRENT_FILE_PATH = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE_PATH.parent.parent

class Settings(BaseSettings):
    BOT_TOKEN: str
    BACKEND_URL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_CHAT_ID: int 
    
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore" 
    )

settings = Settings()