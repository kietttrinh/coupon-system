from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from api.client import api_client

router = Router()

# ================= 1. LẤY THÔNG TIN ADMIN (/me) =================
@router.message(Command("me"))
async def check_me(message: types.Message):
    processing = await message.answer("⏳ Đang tải thông tin...")
    res = await api_client.get_me()
    await processing.delete()
    
    if res["success"]:
        user = res["data"]
        await message.answer(
            f"👤 *THÔNG TIN ADMIN*\n\n"
            f"Tên đăng nhập: `{user.get('username')}`\n"
            f"Email: {user.get('email')}\n"
            f"Quyền hạn: {user.get('role')}"
        )
    else:
        await message.answer("❌ Không thể lấy thông tin. Hãy check lại Backend!")

# ================= 2. DANH SÁCH MÃ (/list_coupons) =================
# ================= 2. DANH SÁCH MÃ (/list_coupons) =================
@router.message(Command("list_coupons"))
async def list_coupons(message: types.Message):
    res = await api_client.get_coupons()
    if not res["success"]:
        return await message.answer("❌ Lỗi lấy danh sách mã.")
    
    data = res["data"]
    items = data if isinstance(data, list) else data.get("items", [])
    
    if not items:
        return await message.answer("📭 Hệ thống chưa có mã giảm giá nào.")

    text = "📋 *DANH SÁCH MÃ GIẢM GIÁ*\n\n"
    for c in items:
        status = "🟢" if c.get("is_active") else "🔴"
        vis = "👁" if c.get("visibility") == "PUBLIC" else "🔒"
        unit = "%" if c.get("discount_type") == "PERCENT" else "đ"
        
        # Xử lý hiển thị min/max để không bị lỗi nếu là None
        min_order = f"{c.get('min_order_value'):,.0f}đ" if c.get("min_order_value") else "0đ"
        max_disc = f"{c.get('max_discount_amount'):,.0f}đ" if c.get("max_discount_amount") else "∞"
        
        # Dòng 1: Tên mã và mức giảm
        text += f"{status} {vis} `{c['code']}` - Giảm {c['discount_value']:,.0f}{unit}\n"
        # Dòng 2: Điều kiện chi tiết
        text += f"   └ Min: {min_order} | Max: {max_disc}\n\n"
    
    await message.answer(text)

# ================= 3. XÓA MÃ (/del_coupon <code) =================
@router.message(Command("del_coupon"))
async def delete_coupon(message: types.Message, command: CommandObject):
    if not command.args:
        return await message.answer("⚠️ Cú pháp: `/del_coupon <MÃ>` (VD: `/del_coupon SALE20`)")
    
    code = command.args.strip()
    find_res = await api_client.get_coupon_by_code(code)
    if not find_res["success"]:
        return await message.answer(find_res["error"])
        
    del_res = await api_client.delete_coupon(find_res["data"]["id"])
    if del_res["success"]:
        await message.answer(f"🗑 Đã xóa vĩnh viễn mã `{code.upper()}`")
    else:
        await message.answer(f"❌ Lỗi xóa mã: {del_res['error']}")

# ================= 4. SỬA MÃ ĐA NĂNG (/edit_coupon) =================
@router.message(Command("edit_coupon"))
async def edit_coupon(message: types.Message, command: CommandObject):
    """
    Cú pháp: /edit_coupon <MÃ> <TRƯỜNG_CẦN_SỬA> <GIÁ_TRỊ_MỚI>
    Ví dụ: 
    /edit_coupon SALE20 is_active false
    /edit_coupon SALE20 max_uses 100
    /edit_coupon SALE20 discount_value 50000
    """
    if not command.args or len(command.args.split()) < 3:
        await message.answer(
            "⚠️ *Cú pháp sai!*\n\n"
            "👉 Dùng lệnh: `/edit_coupon <MÃ> <TRƯỜNG> <GIÁ_TRỊ>`\n\n"
            "Các trường có thể sửa:\n"
            "- `is_active` (true/false): Bật/tắt mã\n"
            "- `discount_value` (số): Đổi giá trị giảm\n"
            "- `min_order_value` (số): Đổi đơn tối thiểu\n"
            "- `visibility` (PUBLIC/PRIVATE)\n"
            "- *(Và các trường thời gian, lượt dùng nếu DB có hỗ trợ)*"
        )
        return

    parts = command.args.split(maxsplit=2)
    code = parts[0].upper()
    field = parts[1].lower()
    value_str = parts[2]

    # 1. Tìm ID của mã cần sửa
    find_res = await api_client.get_coupon_by_code(code)
    if not find_res["success"]:
        return await message.answer(find_res["error"])
    coupon_id = find_res["data"]["id"]

    # 2. Xử lý ép kiểu dữ liệu cho đúng với Backend
    update_data = {}
    if value_str.lower() == "true": update_data[field] = True
    elif value_str.lower() == "false": update_data[field] = False
    elif value_str.isdigit(): update_data[field] = int(value_str)
    else:
        try: update_data[field] = float(value_str)
        except ValueError: update_data[field] = value_str # Giữ nguyên chuỗi

    # 3. Gửi API Cập nhật
    processing = await message.answer("⏳ Đang cập nhật...")
    res = await api_client.update_coupon(coupon_id, update_data)
    await processing.delete()

    if res["success"]:
        await message.answer(f"✅ Đã cập nhật mã `{code}`:\n`{field}` ➡️ `{value_str}`")
    else:
        await message.answer(f"❌ Lỗi: Backend từ chối cập nhật.\nChi tiết: {res['error']}")

@router.message(Command("view_coupon"))
async def view_coupon(message: types.Message, command: CommandObject):
    if not command.args:
        return await message.answer("⚠️ Cú pháp: `/view_coupon <MÃ>` (VD: `/view_coupon SALE20`)")
    
    code = command.args.strip().upper()
    find_res = await api_client.get_coupon_by_code(code)
    
    if not find_res["success"]:
        return await message.answer(find_res["error"])
        
    c = find_res["data"]
    status_text = "🟢 Đang Bật" if c.get("is_active") else "🔴 Đang Tắt"
    vis_text = "Công khai (PUBLIC)" if c.get("visibility") == "PUBLIC" else "Nội bộ (PRIVATE)"
    unit = "%" if c.get("discount_type") == "PERCENT" else "VNĐ"
    
    min_val = f"{c.get('min_order_value'):,.0f} VNĐ" if c.get('min_order_value') else "Không yêu cầu"
    max_val = f"{c.get('max_discount_amount'):,.0f} VNĐ" if c.get('max_discount_amount') else "Không giới hạn"

    # Định dạng ngày tháng nếu Backend có trả về
    created_at = c.get("create_at") or c.get("created_at") or "Không rõ"
    
    detail_text = (
        f"🔎 *CHI TIẾT MÃ: `{code}`*\n\n"
        f"⚙️ *Loại mã:* {c.get('discount_type')}\n"
        f"💰 *Mức giảm:* {c.get('discount_value'):,.0f} {unit}\n"
        f"🛒 *Đơn tối thiểu:* {min_val}\n"
        f"🛑 *Giảm tối đa:* {max_val}\n"
        f"👁 *Hiển thị:* {vis_text}\n"
        f"🚦 *Trạng thái:* {status_text}\n"
    )
    
    # Nếu API Backend có trả về ID và Ngày tháng thì in thêm
    if "id" in c:
        detail_text += f"\n🆔 *Database ID:* {c['id']}"
    if created_at != "Không rõ":
        # Format cắt bỏ phần T và đuôi microsecond đi cho đẹp (Ví dụ: 2026-05-14T23:01:31.123456 -> 2026-05-14 23:01:31)
        clean_date = str(created_at).replace("T", " ")[:19]
        detail_text += f"\n📅 *Ngày tạo:* {clean_date}"

    await message.answer(detail_text)