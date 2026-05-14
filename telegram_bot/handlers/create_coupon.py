from aiogram import Router, F, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states.forms import CreateCouponState
from keyboards.reply import get_discount_type_keyboard, get_skip_keyboard, get_visibility_keyboard
from api.client import api_client

router = Router()

# ================= Bước 1: Nhận lệnh /add_coupon (Hỗ trợ 2 chế độ) =================
@router.message(Command("add_coupon"))
async def start_add_coupon(message: types.Message, state: FSMContext, command: CommandObject):
    if command.args:
        try:
            parts = command.args.split()
            if len(parts) < 6:
                await message.answer(
                    "⚠️ *Thiếu thông tin tạo nhanh!*\n\n"
                    "👉 *Cú pháp:* `/add_coupon <MÃ> <LOẠI> <GIẢM> <ĐƠN_MIN> <MAX_GIẢM> <TRẠNG_THÁI>`\n"
                    "📝 *Ví dụ:* `/add_coupon SALE20 PERCENT 20 500000 150000 PUBLIC`\n"
                    "*(Nếu không yêu cầu Min/Max, hãy điền số 0)*"
                )
                return

            coupon_payload = {
                "code": parts[0].upper(),
                "discount_type": parts[1].upper(),
                "discount_value": float(parts[2]),
                "is_active": True,
                "visibility": parts[5].upper()
            }

            min_order = float(parts[3])
            max_discount = float(parts[4])
            
            if min_order > 0: coupon_payload["min_order_value"] = min_order
            if max_discount > 0: coupon_payload["max_discount_amount"] = max_discount

            if coupon_payload["discount_type"] not in ["PERCENT", "FIXED"]:
                await message.answer("⚠️ Loại mã chỉ được là PERCENT hoặc FIXED.")
                return
            if coupon_payload["visibility"] not in ["PUBLIC", "PRIVATE"]:
                await message.answer("⚠️ Trạng thái chỉ được là PUBLIC hoặc PRIVATE.")
                return

            processing_msg = await message.answer("⏳ Đang xử lý tạo nhanh...")
            result = await api_client.create_coupon(coupon_payload)
            await processing_msg.delete()

            if result["success"]:
                min_txt = f"{min_order:,.0f} đ" if min_order > 0 else "Không"
                max_txt = f"{max_discount:,.0f} đ" if max_discount > 0 else "Không"
                unit = "%" if coupon_payload['discount_type'] == "PERCENT" else "đ"
                
                await message.answer(
                    f"⚡ *Tạo siêu tốc thành công!*\n\n"
                    f"🏷 *Mã:* `{coupon_payload['code']}`\n"
                    f"⚙️ *Loại:* {coupon_payload['discount_type']} | 👁 {coupon_payload['visibility']}\n"
                    f"💰 *Giảm:* {coupon_payload['discount_value']:,.0f} {unit}\n"
                    f"🛒 *Đơn Min:* {min_txt} | 🛑 *Giảm Max:* {max_txt}"
                )
            else:
                await message.answer(f"❌ *Lỗi hệ thống:*\n{result['error']}")

        except ValueError:
            await message.answer("⚠️ Lỗi kiểu dữ liệu: Vị trí của Giá trị giảm, Đơn Min, Giảm Max bắt buộc phải là số!")

        return 

    # CHẾ ĐỘ 2: TẠO TỪNG BƯỚC (FSM - Nếu Admin chỉ gõ /add_coupon)
    await state.set_state(CreateCouponState.waiting_for_code)
    await message.answer(
        "📝 *Tạo mã giảm giá mới*\n\n"
        "Nhập mã bạn muốn tạo (Ví dụ: `SALE20`, `GIAM50K`):",
        reply_markup=ReplyKeyboardRemove()
    )

# ================= Bước 2: Nhận Mã & Hỏi Loại =================
@router.message(CreateCouponState.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    # Lưu mã vào bộ nhớ tạm
    await state.update_data(code=message.text.upper().strip())
    
    await state.set_state(CreateCouponState.waiting_for_type)
    await message.answer(
        "Chọn loại giảm giá:",
        reply_markup=get_discount_type_keyboard()
    )

# ================= Bước 3: Nhận Loại & Hỏi Giá Trị =================
@router.message(CreateCouponState.waiting_for_type)
async def process_type(message: types.Message, state: FSMContext):
    discount_type = message.text.upper()
    if discount_type not in ["PERCENT", "FIXED"]:
        await message.answer("⚠️ Vui lòng chỉ chọn PERCENT hoặc FIXED bằng nút bấm bên dưới!")
        return
        
    await state.update_data(discount_type=discount_type)
    await state.set_state(CreateCouponState.waiting_for_value)
    
    unit = "%" if discount_type == "PERCENT" else "VNĐ"
    await message.answer(
        f"Nhập giá trị giảm (Đơn vị: {unit}):\n"
        f"*(Chỉ nhập số, ví dụ: 20 hoặc 50000)*",
        reply_markup=ReplyKeyboardRemove()
    )

# ================= Bước 4: Nhận Giá Trị & Hỏi Đơn Tối Thiểu =================
@router.message(CreateCouponState.waiting_for_value)
async def process_value(message: types.Message, state: FSMContext):
    try:
        value = float(message.text)
    except ValueError:
        await message.answer("⚠️ Lỗi: Vui lòng chỉ nhập số!")
        return

    await state.update_data(discount_value=value)
    await state.set_state(CreateCouponState.waiting_for_min_order)
    await message.answer(
        "Nhập giá trị đơn hàng tối thiểu để áp dụng mã (VNĐ):\n"
        "*(Bấm nút 'Bỏ qua' nếu không yêu cầu)*",
        reply_markup=get_skip_keyboard()
    )

# ================= Bước 5: Nhận Min Order & Điều hướng =================
@router.message(CreateCouponState.waiting_for_min_order)
async def process_min_order(message: types.Message, state: FSMContext):
    if message.text != "Bỏ qua":
        try:
            min_order = float(message.text)
            await state.update_data(min_order_value=min_order)
        except ValueError:
            await message.answer("⚠️ Lỗi: Vui lòng chỉ nhập số hoặc bấm 'Bỏ qua'!")
            return

    user_data = await state.get_data()
    
    # Nếu là FIXED -> Bỏ qua Max Discount, hỏi luôn Visibility
    if user_data.get("discount_type") == "FIXED":
        await state.set_state(CreateCouponState.waiting_for_visibility)
        await message.answer(
            "Mã này là Công khai (PUBLIC) hay Bí mật (PRIVATE)?",
            reply_markup=get_visibility_keyboard()
        )
    # Nếu là PERCENT -> Phải hỏi Max Discount
    else:
        await state.set_state(CreateCouponState.waiting_for_max_discount)
        await message.answer(
            "Nhập mức giảm tối đa cho phép (VNĐ):\n"
            "*(Bấm nút 'Bỏ qua' nếu không giới hạn)*",
            reply_markup=get_skip_keyboard()
        )

# ================= Bước 6: Nhận Max Discount & Hỏi Visibility =================
@router.message(CreateCouponState.waiting_for_max_discount)
async def process_max_discount(message: types.Message, state: FSMContext):
    if message.text != "Bỏ qua":
        try:
            max_discount = float(message.text)
            await state.update_data(max_discount_amount=max_discount)
        except ValueError:
            await message.answer("⚠️ Lỗi: Vui lòng chỉ nhập số hoặc bấm 'Bỏ qua'!")
            return
            
    await state.set_state(CreateCouponState.waiting_for_visibility)
    await message.answer(
        "Mã này là Công khai (PUBLIC) hay Bí mật (PRIVATE)?",
        reply_markup=get_visibility_keyboard()
    )

# ================= Bước 7: Nhận Visibility & CHỐT ĐƠN =================
@router.message(CreateCouponState.waiting_for_visibility)
async def process_visibility(message: types.Message, state: FSMContext):
    visibility = message.text.upper()
    if visibility not in ["PUBLIC", "PRIVATE"]:
        await message.answer("⚠️ Vui lòng chỉ chọn PUBLIC hoặc PRIVATE bằng nút bấm!")
        return
        
    await state.update_data(visibility=visibility)
    
    # Kích hoạt hàm lưu lên Backend
    await finalize_coupon(message, state)

# ================= Hàm Xử Lý Gọi API =================
async def finalize_coupon(message: types.Message, state: FSMContext):
    # Lấy toàn bộ dữ liệu đã thu thập
    data = await state.get_data()
    
    # Chuẩn bị JSON gửi lên FastAPI
    coupon_payload = {
        "code": data["code"],
        "discount_type": data["discount_type"],
        "discount_value": data["discount_value"],
        "is_active": True,
        "visibility": data["visibility"]
    }
    
    if "min_order_value" in data:
        coupon_payload["min_order_value"] = data["min_order_value"]
    if "max_discount_amount" in data:
        coupon_payload["max_discount_amount"] = data["max_discount_amount"]

    # Xóa trạng thái FSM ngay lập tức (Để Bot không bị kẹt ở lệnh này)
    await state.clear()
    
    # Hiển thị tin nhắn chờ
    processing_msg = await message.answer("⏳ Đang gửi dữ liệu lên hệ thống...", reply_markup=ReplyKeyboardRemove())
    
    # Gọi API
    result = await api_client.create_coupon(coupon_payload)
    
    # Xóa tin nhắn chờ đi cho sạch giao diện
    await processing_msg.delete()
    
    # Trả kết quả (Lưu ý: Chỉ dùng 1 dấu * để in đậm, tránh lỗi Telegram Markdown)
    if result["success"]:
        await message.answer(
            f"✅ *Tạo mã thành công!*\n\n"
            f"🏷 *Mã:* `{coupon_payload['code']}`\n"
            f"⚙️ *Loại:* {coupon_payload['discount_type']}\n"
            f"💰 *Giảm:* {coupon_payload['discount_value']}\n"
            f"👁 *Trạng thái:* {coupon_payload['visibility']}"
        )
    else:
        await message.answer(f"❌ *Lỗi tạo mã:*\n{result['error']}")