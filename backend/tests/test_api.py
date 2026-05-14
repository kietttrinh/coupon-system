"""
Comprehensive End-to-End Test Suite for Coupon System API.
"""
import pytest

def test_comprehensive_system_flow(client):
    """
    Comprehensive Test Scenario: Simulates the journey from system setup to user purchase.
    """
    print("\n--- STARTING COMPREHENSIVE TEST ---")

    # =========================================================================
    # PHASE 1: AUTHENTICATION & AUTHORIZATION (Create Admin and Regular User)
    # =========================================================================
    # 1.1 Create and login Admin
    reg_admin = client.post("/api/v1/auth/register", json={
        "email": "admin@shop.com", "username": "superadmin", 
        "password": "password123", "role": "ADMIN"
    })
    # Use .text to print detailed errors if registration fails
    assert reg_admin.status_code == 201, f"Admin creation error: {reg_admin.text}"
    
    login_admin = client.post("/api/v1/auth/login", data={"username": "superadmin", "password": "password123"})
    assert login_admin.status_code == 200, f"Admin login error: {login_admin.text}"
    admin_token = login_admin.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1.2 Create and login Regular User
    reg_user = client.post("/api/v1/auth/register", json={
        "email": "user@shop.com", "username": "normaluser", 
        "password": "password123", "role": "USER"
    })
    assert reg_user.status_code == 201, f"User creation error: {reg_user.text}"
    
    login_user = client.post("/api/v1/auth/login", data={"username": "normaluser", "password": "password123"})
    assert login_user.status_code == 200, f"User login error: {login_user.text}"
    user_token = login_user.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 1.3 Check fetching Profile
    me_resp = client.get("/api/v1/auth/me", headers=user_headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "normaluser"

    # =========================================================================
    # PHASE 2: PRODUCTS MANAGEMENT
    # =========================================================================
    # 2.1 Admin creates 2 products
    prod1 = client.post("/api/v1/products/", headers=admin_headers, json={
        "name": "Gaming Laptop", "price": 20000000, "stock": 5, "is_active": True
    }).json()
    prod2 = client.post("/api/v1/products/", headers=admin_headers, json={
        "name": "Wireless Mouse", "price": 500000, "stock": 50, "is_active": True
    }).json()

    # 2.2 Regular User fetches product list (Test Pagination)
    list_prods = client.get("/api/v1/products/?skip=0&limit=10", headers=user_headers).json()
    assert list_prods["total"] == 2
    assert len(list_prods["items"]) == 2

    # 2.3 Regular User checks stock
    stock_resp = client.get(f"/api/v1/products/{prod1['id']}/stock", headers=user_headers).json()
    assert stock_resp["stock"] == 5
    assert stock_resp["available"] is True

    # 2.4 Security: Regular user attempts to create a product -> Must be blocked
    # Since our get_current_admin dependency throws 400 "Not enough privileges"
    forbidden_resp = client.post("/api/v1/products/", headers=user_headers, json={
        "name": "Hack Product", "price": 0, "stock": 100, "is_active": True
    })
    assert forbidden_resp.status_code >= 400 

    # =========================================================================
    # PHASE 3: COUPONS MANAGEMENT (Fixed & Percent)
    # =========================================================================
    # 3.1 Admin creates Fixed coupon: 500k off, minimum order 5 million
    fixed_coupon = client.post("/api/v1/coupons/", headers=admin_headers, json={
        "code": "500KOFF", "discount_type": "FIXED", "discount_value": 500000, 
        "min_order_value": 5000000, "is_active": True, "visibility": "PUBLIC"
    }).json()

    # 3.2 Admin creates Percent coupon: 10% off, Max 300k, minimum order 1 million
    percent_coupon = client.post("/api/v1/coupons/", headers=admin_headers, json={
        "code": "SALE10", "discount_type": "PERCENT", "discount_value": 10, 
        "min_order_value": 1000000, "max_discount_amount": 300000, 
        "is_active": True, "visibility": "PUBLIC"
    }).json()

    # =========================================================================
    # PHASE 4: THE PRICING ENGINE (Calculation Core)
    # =========================================================================
    # 4.1 Customer buys Mouse for 500k, applies 500KOFF -> Must be rejected (minimum is 5 million)
    val1 = client.post("/api/v1/coupons/validate", headers=user_headers, json={
        "code": "500KOFF", "order_value": 500000
    })
    assert val1.status_code == 400
    assert "Minimum order value" in val1.json()["detail"]

    # 4.2 Customer buys Laptop for 20 million, applies 500KOFF -> Valid, final price = 19.5 million
    val2 = client.post("/api/v1/coupons/validate", headers=user_headers, json={
        "code": "500KOFF", "order_value": 20000000
    }).json()
    assert val2["is_valid"] is True
    assert val2["discount_amount"] == 500000
    assert val2["final_price"] == 19500000

    # 4.3 Customer buys Laptop for 20 million, applies SALE10 -> 10% off is 2 million, but capped at Max 300k
    val3 = client.post("/api/v1/coupons/validate", headers=user_headers, json={
        "code": "SALE10", "order_value": 20000000
    }).json()
    assert val3["is_valid"] is True
    assert val3["discount_amount"] == 300000  # <--- Test Max Discount cap!
    assert val3["final_price"] == 19700000

    # =========================================================================
    # PHASE 5: GREEDY DYNAMIC SORTING (Recommendation Core)
    # =========================================================================
    # User has a 20 million cart, asks the system which code is the most beneficial?
    # In reality: 
    # - 500KOFF -> 500k off
    # - SALE10 -> 300k off (due to max cap)
    # Greedy algorithm must rank 500KOFF at number 1.
    recommend_resp = client.get("/api/v1/coupons/recommend?order_value=20000000", headers=user_headers)
    assert recommend_resp.status_code == 200
    recommendations = recommend_resp.json()
    
    assert len(recommendations) == 2
    assert recommendations[0]["code"] == "500KOFF" # 500k off code must be at the top
    assert recommendations[1]["code"] == "SALE10"   # 300k off code must be second

    # =========================================================================
    # PHASE 6: ADMIN CLEANUP (Delete data)
    # =========================================================================
    del_resp = client.delete(f"/api/v1/coupons/{fixed_coupon['id']}", headers=admin_headers)
    assert del_resp.status_code == 200

    print("ALL FLOWS EXECUTED PERFECTLY!")