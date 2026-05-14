from aiogram import Router, types
from aiogram.filters import CommandStart

# Khởi tạo một Router riêng cho các lệnh cơ bản
router = Router()

@router.message(CommandStart())
async def command_start_handler(message: types.Message):
    """
    /start command
    """
    chat_id = message.chat.id
    
    welcome_text = (
        f"Xin chào Admin! 👋\n\n"
        f"🤖 **Hệ thống Quản lý Coupon** đã sẵn sàng nhận lệnh.\n"
        f"🆔 Chat ID của bạn là: `{chat_id}`\n\n"
        f"*(Hãy giữ bí mật Chat ID này và cấu hình vào file .env nhé)*"
    )
    
    # Gửi tin nhắn trả lời
    await message.answer(welcome_text, parse_mode="Markdown")