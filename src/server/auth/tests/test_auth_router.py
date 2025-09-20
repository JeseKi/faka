# -*- coding: utf-8 -*-
import os
from typing import Dict, Any


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


def test_register_and_login_flow(test_client):
    # 注册
    register_user_helper(test_client, "alice", "alice@example.com", "Password123")

    # 登录
    resp = test_client.post(
        "/api/auth/login", json={"username": "alice", "password": "Password123"}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data and "refresh_token" in data


def test_login_wrong_password(test_client, init_test_database):
    resp = test_client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_profile_with_test_token(test_client, init_test_database):
    os.environ.setdefault("APP_ENV", "test")
    # 使用 test_token 直接访问
    resp = test_client.get(
        "/api/auth/profile",
        headers={"Authorization": "Bearer KISPACE_TEST_TOKEN"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "admin"


def test_change_password_flow(test_client):
    # 注册
    register_user_helper(test_client, "bob", "bob@example.com", "OldPassword123")
    # 登录
    login = test_client.post(
        "/api/auth/login", json={"username": "bob", "password": "OldPassword123"}
    ).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    # 修改密码：旧密码错误
    resp = test_client.put(
        "/api/auth/password",
        json={"old_password": "wrong", "new_password": "NewPassword123"},
        headers=headers,
    )
    assert resp.status_code == 400

    # 修改密码：成功
    resp = test_client.put(
        "/api/auth/password",
        json={"old_password": "OldPassword123", "new_password": "NewPassword123"},
        headers=headers,
    )
    assert resp.status_code == 200

    # 新密码登录
    resp = test_client.post(
        "/api/auth/login", json={"username": "bob", "password": "NewPassword123"}
    )
    assert resp.status_code == 200