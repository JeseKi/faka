# -*- coding: utf-8 -*-
"""
订单路由层测试
"""

def test_verify_activation_code_flow(test_client, test_db_session):
    """测试验证卡密并创建订单流程"""
    # 先创建一个卡密
    from src.server.activation_code.service import create_activation_codes
    code = create_activation_codes(test_db_session, "Test Card", 1)
    
    # 注册一个用户
    register_resp = test_client.post(
        "/api/auth/register",
        json={
            "username": "order_user",
            "email": "order_user@example.com",
            "password": "Password123",
        },
    )
    assert register_resp.status_code == 201
    
    # 用户登录
    login_resp = test_client.post(
        "/api/auth/login",
        json={"username": "order_user", "password": "Password123"}
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 验证卡密并创建订单
    verify_resp = test_client.post(
        "/api/orders/verify",
        json={"code": code[0].code},
        headers=headers
    )
    assert verify_resp.status_code == 201
    order_data = verify_resp.json()
    assert "id" in order_data
    assert order_data["activation_code"] == code[0].code
    assert order_data["status"] == "pending"


def test_get_my_orders(test_client, test_db_session):
    """测试获取当前用户订单列表"""
    # 注册一个用户
    register_resp = test_client.post(
        "/api/auth/register",
        json={
            "username": "order_user2",
            "email": "order_user2@example.com",
            "password": "Password123",
        },
    )
    assert register_resp.status_code == 201
    
    # 用户登录
    login_resp = test_client.post(
        "/api/auth/login",
        json={"username": "order_user2", "password": "Password123"}
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 获取我的订单列表（应该为空）
    orders_resp = test_client.get("/api/orders/me", headers=headers)
    assert orders_resp.status_code == 200
    orders_data = orders_resp.json()
    assert isinstance(orders_data, list)
    # 初始应该没有订单
    assert len(orders_data) == 0


def test_get_order_stats(test_client):
    """测试获取订单统计信息"""
    # 管理员登录（使用test token）
    import os
    os.environ.setdefault("APP_ENV", "test")
    
    stats_resp = test_client.get(
        "/api/orders/stats",
        headers={"Authorization": "Bearer KISPACE_TEST_TOKEN"}
    )
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert "total_orders" in stats_data
    assert "pending_orders" in stats_data
    assert "completed_orders" in stats_data