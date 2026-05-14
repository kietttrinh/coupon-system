import httpx
import logging
from typing import Dict, Any, Optional

from config import settings

logger = logging.getLogger(__name__)

class BackendAPIClient:
    def __init__(self):
        self.base_url = settings.BACKEND_URL
        self.token: Optional[str] = None

    async def login(self) -> bool:
        login_url = f"{self.base_url}/auth/login"
        
        login_data = {
            "username": settings.ADMIN_USERNAME,
            "password": settings.ADMIN_PASSWORD
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(login_url, data=login_data)
                response.raise_for_status() # Nếu lỗi (4xx, 5xx) sẽ ném exception ngay
                
                # Trích xuất access_token từ JSON trả về
                self.token = response.json().get("access_token")
                logger.info("✅ Đã đăng nhập Backend và lấy token thành công!")
                return True
                
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ Lỗi đăng nhập Backend (Mã {e.response.status_code}): {e.response.text}")
                return False
            except httpx.RequestError as e:
                logger.error(f"🔌 Không thể kết nối đến Backend (Backend chưa bật?): {e}")
                return False

    def _get_headers(self) -> Dict[str, str]:
        """Hàm nội bộ để sinh header chứa Token"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    async def create_coupon(self, coupon_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gọi API tạo Mã giảm giá mới.
        """
        if not self.token:
            success = await self.login()
            if not success:
                return {"success": False, "error": "Bot không thể đăng nhập vào Backend. Hãy check log!"}

        url = f"{self.base_url}/coupons/"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=coupon_data, headers=self._get_headers())
            
            if response.status_code == 401:
                logger.warning("⚠️ Token đã hết hạn, Bot tự động đăng nhập lại...")
                login_success = await self.login()
                if login_success:
                    response = await client.post(url, json=coupon_data, headers=self._get_headers())
                else:
                    return {"success": False, "error": "Lỗi xác thực: Đăng nhập lại thất bại!"}

            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            else:
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                    
                return {"success": False, "error": f"Lỗi {response.status_code}: {error_detail}"}

    # ================= AUTH API =================
    async def get_me(self) -> dict:
        """Lấy thông tin Admin hiện tại"""
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/auth/me", headers=self._get_headers())
            return {"success": True, "data": resp.json()} if resp.status_code == 200 else {"success": False}

    # ================= COUPONS API =================
    async def get_coupons(self, skip: int = 0, limit: int = 50) -> dict:
        """Lấy danh sách mã giảm giá"""
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/coupons/?skip={skip}&limit={limit}", headers=self._get_headers())
            return {"success": True, "data": resp.json()} if resp.status_code == 200 else {"success": False}

    async def get_coupon_by_code(self, code: str) -> dict:
        """Hàm tìm ID của coupon dựa vào Code (Vì API PUT/DELETE cần ID)"""
        res = await self.get_coupons(limit=100) # Lấy danh sách để tìm
        if res["success"]:
            data = res["data"]
            # Sửa lại đoạn trích xuất items giống y hệt file manage.py
            items = data if isinstance(data, list) else data.get("items", [])
            
            for c in items: 
                if c["code"].upper() == code.upper():
                    return {"success": True, "data": c}
        return {"success": False, "error": "Không tìm thấy mã này trong hệ thống!"}

    async def update_coupon(self, coupon_id: int, update_data: dict) -> dict:
        """Cập nhật mã giảm giá (Sửa thời gian, lượt dùng, v.v)"""
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.put(f"{self.base_url}/coupons/{coupon_id}", json=update_data, headers=self._get_headers())
            if resp.status_code == 200: return {"success": True, "data": resp.json()}
            return {"success": False, "error": resp.text}

    async def delete_coupon(self, coupon_id: int) -> dict:
        """Xóa mã giảm giá"""
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{self.base_url}/coupons/{coupon_id}", headers=self._get_headers())
            if resp.status_code == 200: return {"success": True}
            return {"success": False, "error": resp.text}

    # ================= PRODUCTS API =================
    async def get_products(self, skip: int = 0, limit: int = 50) -> dict:
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/products/?skip={skip}&limit={limit}", headers=self._get_headers())
            return {"success": True, "data": resp.json()} if resp.status_code == 200 else {"success": False}

    async def get_product(self, product_id: int) -> dict:
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/products/{product_id}", headers=self._get_headers())
            if resp.status_code == 200: return {"success": True, "data": resp.json()}
            return {"success": False, "error": f"Lỗi {resp.status_code}: Không tìm thấy sản phẩm hoặc lỗi server."}

    async def create_product(self, product_data: dict) -> dict:
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/products/", json=product_data, headers=self._get_headers())
            if resp.status_code == 201: return {"success": True, "data": resp.json()}
            return {"success": False, "error": resp.text}

    async def update_product(self, product_id: int, update_data: dict) -> dict:
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.put(f"{self.base_url}/products/{product_id}", json=update_data, headers=self._get_headers())
            if resp.status_code == 200: return {"success": True, "data": resp.json()}
            return {"success": False, "error": resp.text}

    async def delete_product(self, product_id: int) -> dict:
        if not self.token and not await self.login(): return {"success": False}
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{self.base_url}/products/{product_id}", headers=self._get_headers())
            if resp.status_code == 200: return {"success": True}
            return {"success": False, "error": resp.text}

api_client = BackendAPIClient()