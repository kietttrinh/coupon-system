from aiogram.fsm.state import State, StatesGroup

class CreateCouponState(StatesGroup):
    waiting_for_code = State()            # Bước 1: Chờ nhập mã (VD: SALE20)
    waiting_for_type = State()            # Bước 2: Chờ chọn loại (PERCENT / FIXED)
    waiting_for_value = State()           # Bước 3: Chờ nhập giá trị giảm
    waiting_for_min_order = State()       # Bước 4: Chờ nhập đơn tối thiểu (Có thể bỏ qua)
    waiting_for_max_discount = State()    # Bước 5: Chờ nhập mức giảm tối đa (Có thể bỏ qua)
    waiting_for_visibility = State()    

class CreateProductState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_stock = State()