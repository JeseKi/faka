# -*- coding: utf-8 -*-
"""
订单路由层测试
"""

from typing import Dict, Any
import os

from src.server.auth.config import auth_config

os.environ.setdefault("APP_ENV", "dev")


def register_user_helper(
    test_client, username: str, email: str, password: str
) -> Dict[str, Any]:
    """辅助函数：使用新的两步注册流程注册用户"""
    # 1. 发送验证码
    resp = test_client.post("/api/auth/send-verification-code", json={"email": email})
    assert resp.status_code == 200, f"发送验证码失败: {resp.text}"

    # 2. 从服务中获取验证码
    from src.server.auth.service import verification_codes

    code = verification_codes[email]["code"]

    # 3. 使用验证码注册
    resp = test_client.post(
        "/api/auth/register-with-code",
        json={
            "username": username,
            "email": email,
            "password": password,
            "code": code,
        },
    )
    assert resp.status_code == 201, f"注册失败: {resp.text}"
    return resp.json()


def test_get_order_stats(test_client, test_db_session):
    """测试获取订单统计信息"""
    # 确保管理员用户存在
    from src.server.auth.service import bootstrap_default_admin

    bootstrap_default_admin(test_db_session)

    # 管理员登录（使用test token）
    import os

    os.environ.setdefault("APP_ENV", "test")

    stats_resp = test_client.get(
        "/api/orders/stats",
        headers={"Authorization": f"Bearer {auth_config.test_token}"},
    )
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert "total_orders" in stats_data
    assert "pending_orders" in stats_data
    assert "completed_orders" in stats_data


def test_list_processing_orders(test_client, test_db_session):
    """测试获取处理中订单列表"""
    # 确保管理员用户存在
    from src.server.auth.service import bootstrap_default_admin

    bootstrap_default_admin(test_db_session)

    # 管理员登录（使用test token）
    import os

    os.environ.setdefault("APP_ENV", "test")

    processing_orders_resp = test_client.get(
        "/api/orders/processing",
        headers={"Authorization": f"Bearer {auth_config.test_token}"},
    )
    assert processing_orders_resp.status_code == 200
    processing_orders_data = processing_orders_resp.json()
    assert isinstance(processing_orders_data, list)
