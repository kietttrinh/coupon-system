from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states.forms import CreateProductState
from api.client import api_client

router = Router()

# ================= 1. DANH SÁCH SẢN PHẨM =================
@router.message(Command("list_products"))
async def list_products(message: types.Message):
    res = await api_client.get_products()
    if not res["success"]:
        return await message.answer("❌ Lỗi lấy danh sách sản phẩm.")
    
    data = res["data"]
    items = data if isinstance(data, list) else data.get("items", [])
    
    if not items:
        return await message.answer("📭 Chưa có sản phẩm nào trong cửa hàng.")

    text = "📦 *DANH SÁCH SẢN PHẨM*\n\n"
    for p in items:
        status = "🟢" if p.get("is_active", True) else "🔴"
        text += f"{status} ID: `{p['id']}` | *{p['name']}*\n"
        text += f"   └ Giá: {float(p['price']):,.0f}đ | Tồn kho: {p['stock']}\n\n"
    
    await message.answer(text)

# ================= 2. XEM CHI TIẾT SẢN PHẨM =================
@router.message(Command("view_product"))
async def view_product(message: types.Message, command: CommandObject):
    # ... (giữ nguyên phần kiểm tra ID)
    p_id = int(command.args.strip())
    res = await api_client.get_product(p_id)
    if not res["success"]: return await message.answer(res["error"])
        
    p = res["data"]
    status = "🟢 Đang bán" if p.get("is_active", True) else "🔴 Ngừng bán"
    desc = p.get("description") or "Không có mô tả." # Lấy mô tả, nếu null thì in chữ Không có
    
    await message.answer(
        f"🔎 *CHI TIẾT SẢN PHẨM*\n\n"
        f"🆔 ID: `{p['id']}`\n"
        f"📦 Tên: *{p['name']}*\n"
        f"📝 Mô tả: {desc}\n"
        f"💰 Giá: {float(p['price']):,.0f} VNĐ\n"
        f"🏢 Tồn kho: {p['stock']} sản phẩm\n"
        f"🚦 Trạng thái: {status}\n"
    )

# ================= 3. THÊM SẢN PHẨM (Quick / FSM) =================
@router.message(Command("add_product"))
async def add_product(message: types.Message, state: FSMContext, command: CommandObject):
    # CHẾ ĐỘ 1: TẠO SIÊU TỐC
    if command.args:
        try:
            # Cú pháp: /add_product Tên_Sản_Phẩm Giá Tồn_kho Mô tả dài dài phía sau...
            # VD: /add_product Laptop_Gaming 20000000 5 Chống ồn chủ động, led RGB
            parts = command.args.split()
            if len(parts) < 3: raise ValueError
            
            payload = {
                "name": parts[0].replace("_", " "),
                "price": float(parts[1]),
                "stock": int(parts[2]),
                "description": " ".join(parts[3:]) if len(parts) > 3 else "", # Gom hết chữ đằng sau làm mô tả
                "is_active": True
            }
            res = await api_client.create_product(payload)
            if res["success"]:
                await message.answer(f"✅ Tạo thành công:\n*{payload['name']}*\n📝 {payload['description']}")
            else:
                await message.answer(f"❌ Lỗi: {res['error']}")
        except ValueError:
            await message.answer("⚠️ Cú pháp nhanh sai!\nVD: `/add_product Bàn_phím_cơ 1500000 10 Gõ siêu êm`")
        return

    # CHẾ ĐỘ 2: HỎI ĐÁP FSM
    await state.set_state(CreateProductState.waiting_for_name)
    await message.answer("📦 Nhập **Tên sản phẩm** mới:", reply_markup=ReplyKeyboardRemove())

@router.message(CreateProductState.waiting_for_name)
async def p_process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(CreateProductState.waiting_for_price)
    await message.answer("💰 Nhập **Giá bán** (VNĐ - Chỉ ghi số):")

@router.message(CreateProductState.waiting_for_description)
async def p_process_desc(message: types.Message, state: FSMContext):
    desc = message.text.strip()
    if desc.lower() == "bỏ qua":
        desc = ""
        
    await state.update_data(description=desc)
    await state.set_state(CreateProductState.waiting_for_price)
    await message.answer("💰 Nhập **Giá bán** (VNĐ - Chỉ ghi số):")

@router.message(CreateProductState.waiting_for_price)
async def p_process_price(message: types.Message, state: FSMContext):
    try:
        await state.update_data(price=float(message.text))
        await state.set_state(CreateProductState.waiting_for_stock)
        await message.answer("🏢 Nhập số lượng **Tồn kho** (Chỉ ghi số):")
    except ValueError:
        await message.answer("⚠️ Lỗi: Giá phải là chữ số!")

@router.message(CreateProductState.waiting_for_stock)
async def p_process_stock(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        payload = {
            "name": data["name"],
            "description": data.get("description", ""), # Thêm description vào đây
            "price": data["price"],
            "stock": int(message.text),
            "is_active": True
        }
        await state.clear()
        res = await api_client.create_product(payload)
        
        if res["success"]:
            await message.answer(f"✅ Tạo thành công sản phẩm:\n*{payload['name']}*")
        else:
            await message.answer(f"❌ Lỗi tạo sản phẩm: {res['error']}")
    except ValueError:
        await message.answer("⚠️ Lỗi: Số lượng tồn kho phải là số!")

# ================= 4. SỬA SẢN PHẨM =================
@router.message(Command("edit_product"))
async def edit_product(message: types.Message, command: CommandObject):
    # Cú pháp: /edit_product <ID> <TRƯỜNG> <GIÁ_TRỊ>
    if not command.args or len(command.args.split()) < 3:
        return await message.answer("⚠️ Cú pháp: `/edit_product <ID> <TRƯỜNG> <GIÁ_TRỊ>`\nVD: `/edit_product 1 price 1500000`")
    
    parts = command.args.split(maxsplit=2)
    if not parts[0].isdigit(): return await message.answer("⚠️ ID phải là số.")
    
    p_id = int(parts[0])
    field = parts[1].lower()
    val_str = parts[2]
    
    update_data = {}
    if val_str.lower() in ["true", "false"]: update_data[field] = (val_str.lower() == "true")
    elif val_str.isdigit(): update_data[field] = int(val_str)
    else:
        try: update_data[field] = float(val_str)
        except ValueError: update_data[field] = val_str

    res = await api_client.update_product(p_id, update_data)
    if res["success"]: await message.answer(f"✅ Đã cập nhật Sản phẩm ID `{p_id}`:\n`{field}` ➡️ `{val_str}`")
    else: await message.answer(f"❌ Lỗi: {res['error']}")

# ================= 5. XÓA SẢN PHẨM =================
@router.message(Command("del_product"))
async def del_product(message: types.Message, command: CommandObject):
    if not command.args or not command.args.isdigit():
        return await message.answer("⚠️ Cú pháp: `/del_product <ID>` (VD: `/del_product 1`)")
    
    p_id = int(command.args.strip())
    res = await api_client.delete_product(p_id)
    if res["success"]: await message.answer(f"🗑 Đã xóa sản phẩm ID `{p_id}`")
    else: await message.answer(f"❌ Lỗi xóa: {res['error']}")