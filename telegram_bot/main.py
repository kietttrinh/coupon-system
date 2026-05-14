"""
Main handler file for the Telegram bot.

This module contains the primary handler functions for:
- Processing incoming messages from users
- Distinguishing between regular messages and bot commands
- Routing commands to appropriate command handlers
- Handling admin verification before processing privileged commands
- Managing conversation states for multi-step commands
- Sending responses back to users via the Telegram API

The handlers interface with the telegram-bot-python library
and connect to the backend API or database directly
depending on implementation architecture.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import settings
from handlers import start, create_coupon, manage, product  # Import router từ thư mục handlers
from middlewares.auth import AdminCheckMiddleware

async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    dp = Dispatcher()
    
    dp.message.middleware(AdminCheckMiddleware()) # Protect
    dp.include_router(start.router)
    dp.include_router(create_coupon.router)
    dp.include_router(manage.router)
    dp.include_router(product.router)

    print("Starting BOT...")

    commands = [
        BotCommand(command="start", description="Trang chủ"),
        BotCommand(command="me", description="Kiểm tra Auth"),
        BotCommand(command="add_coupon", description="Tạo mã (thêm tham số để tạo nhanh)"),
        BotCommand(command="list_coupons", description="Xem danh sách tất cả mã"),
        BotCommand(command="view_coupon", description="Xem chi tiết 1 mã (VD: /view_coupon SALE20)"), 
        BotCommand(command="edit_coupon", description="Sửa mã (VD: /edit_coupon SALE20 is_active false)"),
        BotCommand(command="del_coupon", description="Xóa mã (VD: /del_coupon SALE20)"),
        BotCommand(command="add_product", description="Thêm sản phẩm mới"),
        BotCommand(command="list_products", description="DS sản phẩm"),
        BotCommand(command="view_product", description="Xem chi tiết sản phẩm (Cần ID)"),
        BotCommand(command="edit_product", description="Sửa sản phẩm (Cần ID)"),
        BotCommand(command="del_product", description="Xóa sản phẩm (Cần ID)")
    ]

    await bot.set_my_commands(commands)
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())