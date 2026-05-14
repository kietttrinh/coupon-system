from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def get_discount_type_keyboard() -> ReplyKeyboardMarkup:
    """Bàn phím chọn loại giảm giá"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="PERCENT"), KeyboardButton(text="FIXED")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_skip_keyboard() -> ReplyKeyboardMarkup:
    """Bàn phím có nút Bỏ qua"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Bỏ qua")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_visibility_keyboard() -> ReplyKeyboardMarkup:
    """Bàn phím chọn trạng thái hiển thị"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="PUBLIC"), KeyboardButton(text="PRIVATE")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )