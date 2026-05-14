from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from config import settings

class AdminCheckMiddleware(BaseMiddleware):
    """
    Middleware kiểm tra quyền truy cập.
    Mọi tin nhắn đều phải qua đây trước khi đến các Handler.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        user_id = event.from_user.id
        
        if user_id != settings.ADMIN_CHAT_ID:
            await event.answer(
                "⛔ *CẢNH BÁO AN NINH*\n\n"
                "Bạn không có quyền truy cập vào hệ thống này. "
                "Hành động của bạn đã bị từ chối."
            )
            return 
            
        return await handler(event, data)