## PROPOSAL PROJECT

### 1. Kiến trúc 
*   **Frontend:** HTML5, CSS3, Vanilla Javascript. Giao tiếp với server qua Fetch API.
*   **Backend:** Python 3.x, FastAPI. 
*   **Database:** MySQL.
*   **Quản trị hệ thống (Admin):** Telegram Bot API (Webhook - FastAPI).

---

### 2. Databases

| Bảng (Table) | Cột (Columns) | Kiểu dữ liệu & Ràng buộc | Chức năng |
| :--- | :--- | :--- | :--- |
| **Users** | `id`, `username`, `password_hash`, `role`, `telegram_chat_id` | `role`: ENUM('user', 'admin')<br>`telegram_chat_id`: VARCHAR (Nullable) | Định danh tài khoản. `telegram_chat_id` dùng để Bot xác thực quyền Admin khi nhận lệnh điều khiển. |
| **Products** | `id`, `name`, `base_price`, `stock` | `base_price`: DECIMAL<br>`stock`: INT | Lưu trữ thông tin và số lượng tồn kho sản phẩm. |
| **Coupons** | `id`, `code`, `visibility`, `discount_type`, `discount_value`, `max_discount_amount`, `min_order_value` | `visibility`: ENUM('PUBLIC', 'PRIVATE')<br>`discount_type`: ENUM('FIXED', 'PERCENT')<br>`max_discount_amount`: DECIMAL (NULL)<br>`min_order_value`: DECIMAL | Cấu hình động mọi loại khuyến mãi. `PUBLIC` hiển thị trên UI, `PRIVATE` yêu cầu người dùng tự nhập mã. |
| **Coupon_Schedules** | `id`, `coupon_id`, `start_time`, `end_time` | FK: `coupon_id` tham chiếu `Coupons.id` | Quản lý đa khung giờ áp dụng cho một mã giảm giá. |
| **Usage_Logs** | `id`, `user_id`, `coupon_id`, `used_at` | FK: `user_id`, `coupon_id` | Ghi nhận lịch sử để kiểm soát giới hạn (ví dụ: mỗi user 1 lần/mã). |

---

### 3. Phân tích Thuật toán & Logic Cốt lõi (Core Business Logic)

#### 3.1. Overlap processing (Merge Intervals)
Được kích hoạt khi Admin thêm khung giờ mới $[start_{new}, end_{new}]$ vào bảng `Coupon_Schedules` thông qua Telegram. Đảm bảo một mã không có 2 khoảng thời gian hiệu lực đè lên nhau.

*   **Thuật toán:**
    1. Truy vấn DB lấy tập hợp $S$ gồm $N$ khoảng thời gian hiện tại của `coupon_id`.
    2. Thêm $[start_{new}, end_{new}]$ vào $S$.
    3. Sắp xếp $S$ theo `start_time` tăng dần. Độ phức tạp: $O(N \log N)$ | $O(N)$.
    4. Duyệt tuyến tính qua $S$. Nếu tồn tại chỉ số $i$ sao cho $start_i \le end_{i-1}$, hệ thống kết luận xảy ra chồng chéo (Collapse). Độ phức tạp: $O(N)$.
*   **Xử lý:** Bắn Exception (HTTP 400), Bot Telegram trả thông báo lỗi chi tiết cho Admin, hủy thao tác INSERT vào CSDL.

#### 3.2. Recommend coupons system (Greedy Dynamic Sorting)
Được kích hoạt khi Client mở giao diện xem danh sách các mã `PUBLIC`. Hệ thống luôn đẩy mã giảm nhiều tiền nhất lên đầu để gợi ý.

*   **Thuật toán:**
    1. **Input:** `current_price` của đơn hàng/sản phẩm; danh sách các coupon đang thỏa mãn điều kiện thời gian và `visibility = 'PUBLIC'`.
    2. Lọc bỏ các mã có `min_order_value > current_price`.
    3. Với mỗi mã còn lại, ánh xạ (Map) hàm tính `actual_discount` (Xem mục 3.3).
    4. Sắp xếp (Sort) danh sách giảm dần theo khóa `actual_discount`. Độ phức tạp: $O(K \log K)$ với $K$ là số mã hợp lệ.
    5. **Output:** Trả về danh sách JSON.



#### 3.3. Động cơ tính giá (Pricing Engine)
Hàm xử lý tập trung mọi tham số từ bảng `Coupons` để tính ra số tiền được giảm. Hàm này có tính đa hình đối với cấu trúc dữ liệu.

1. Kiểm tra điều kiện: Giá gốc $<$ min_order_value $\rightarrow$ Từ chối.
2. Tính mức giảm (discount_amount):
- Nếu `FIXED`: `discount_amount = discount_value`.
- Nếu `PERCENTAGE`: `discount_amount =` Giá gốc $\times$ `(discount_value / $100$)`. Cắt ngọn nếu có `max_discount_amount`.
3. Hợp lệ hóa: Đảm bảo Giá cuối $\ge 0$.

```python
def calculate_discount(current_price: float, coupon: dict) -> float:
    # Reject
    if coupon.get('min_order_value') and current_price < coupon['min_order_value']:
        return 0.0

    discount_amount = 0.0

    # FIXED coupon
    if coupon['discount_type'] == 'FIXED':
        discount_amount = coupon['discount_value']

    # PERCENT coupon
    elif coupon['discount_type'] == 'PERCENT':
        discount_amount = current_price * (coupon['discount_value'] / 100)
        # Max discount
        if coupon.get('max_discount_amount'):
            discount_amount = min(discount_amount, coupon['max_discount_amount'])

    return min(discount_amount, current_price)
```

---

### 4. Flow

#### 4.1. Giao diện Client (Frontend)
*   **Danh sách sản phẩm:** Render dạng Grid/Card chuẩn E-commerce.
*   **Khu vực Coupon:**
    *   **Mã Public:** Gọi API `GET /api/coupons?price=...` để nhận danh sách đã được thuật toán (3.2) sắp xếp. UI highlight mã ở Index 0 (Lời nhất).
    *   **Mã Private:** Cung cấp Input Text để người dùng tự gõ mã ẩn.
*   **Đồng bộ thời gian:** Dùng `setInterval` check đồng hồ Client so với `start_time` và `end_time`. Nút "Áp dụng" bị `disabled` nếu chưa đến giờ.

#### 4.2. Luồng xác thực thanh toán (Server-side Validation)
Không tin tưởng thời gian và logic trên JS. Khi User submit Request áp mã/mua hàng, Backend kiểm tra nghiêm ngặt 4 lớp (Độ phức tạp truy vấn DB: $O(1)$ cho mỗi điều kiện có Index):
1.  **Tính hợp lệ của Mã:** `code` có tồn tại không?
2.  **Ràng buộc thời gian:** Truy vấn `Current_Server_Time` có nằm trong bất kỳ $[start_i, end_i]$ nào của bảng `Coupon_Schedules` không?
3.  **Điều kiện kinh doanh:** `Products.stock > 0` và User chưa có bản ghi trùng `coupon_id` trong `Usage_Logs`.
4.  **Tính lại giá trị:** Gọi hàm (3.3) để tính lại giá cuối cùng trước khi ghi vào CSDL.

#### 4.3. Quản trị qua Telegram Bot
*   Webhook nhận POST request từ Telegram server.
*   Trích xuất `chat_id`. Query bảng `Users` kiểm tra quyền (Phải là `admin`).
*   **Lệnh `/create_coupon`:** Nhận tham số tạo bản ghi mới vào bảng `Coupons` (Gán cờ Public/Private, Max Amount, Min Order).
*   **Lệnh `/add_time`:** Kích hoạt thuật toán (3.1). Nếu Passed, chèn bản ghi vào `Coupon_Schedules`. Trả kết quả về chat.

---

### 5. Lộ trình triển khai (Implementation Plan)

*   **Giai đoạn 1 (Database & Algorithms):** Viết script tạo Database MySQL. Xây dựng các hàm Python độc lập (Core Engine) xử lý thuật toán Merge Intervals và Pricing. Thực hiện Unit Test trên các hàm này với các case ranh giới (Edge cases).
*   **Giai đoạn 2 (Backend APIs):** Thiết lập FastAPI. Viết các endpoint RESTful xử lý thao tác GET sản phẩm, tính toán mã Public tốt nhất, và POST thanh toán. Tích hợp Core Engine ở Giai đoạn 1 vào các endpoint.
*   **Giai đoạn 3 (Telegram Bot):** Tạo Bot qua BotFather. Xây dựng endpoint `/webhook`. Viết bộ Parser phân tích cú pháp tin nhắn của Admin để gọi các hàm cập nhật CSDL tương ứng.
*   **Giai đoạn 4 (Frontend UI):** Thiết kế giao diện bằng HTML/CSS/JS thuần. Viết các hàm Fetch API để lấy dữ liệu động và xử lý logic `setInterval` cho các button áp dụng mã.

---

### 6. Đánh giá & Hướng mở rộng

*   **Ưu điểm (Pros):** Thiết kế CSDL mạnh mẽ, bao quát được các nghiệp vụ khuyến mãi phức tạp nhất. Tách biệt rõ ràng tầng dữ liệu, thuật toán và API. Áp dụng DSA vào bài toán thực tế giúp nâng cao hiệu suất xử lý ở Backend thay vì đẩy tải xuống CSDL.
*   **Nhược điểm (Cons):** Chênh lệch thời gian (Time Drift) giữa Client và Server có thể gây ra trải nghiệm lỗi (UI báo mã khả dụng nhưng Server báo lỗi vì chưa đến giờ do lệch giây).
*   **Hướng mở rộng (Future Scope):**
    1.  **Concurrency Management:** Khi 2 Users áp mã vào cùng 1 mili-giây cho sản phẩm có `stock = 1`, cần thiết lập Database Transaction Isolation ở mức `SERIALIZABLE` hoặc dùng Redis Lock để ngăn chặn Race Condition.
    2.  **WebSockets:** Thay thế `setInterval` ở Frontend bằng kết nối Socket để Backend chủ động đẩy (Push) event thay đổi trạng thái Coupon, giải quyết triệt để vấn đề lệch giờ.