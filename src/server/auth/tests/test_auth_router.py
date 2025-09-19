# -*- coding: utf-8 -*-
import os


def test_register_and_login_flow(test_client):
    # 注册
    resp = test_client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123",
        },
    )
    assert resp.status_code == 201, resp.text

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
    test_client.post(
        "/api/auth/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "OldPassword123",
        },
    )
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


def test_send_verification_code_flow(test_client):
    # 发送验证码
    resp = test_client.post(
        "/api/auth/send-verification-code",
        json={"email": "verify@example.com"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert data["message"] == "验证码已发送"


def test_send_verification_code_already_registered(test_client):
    # 先注册一个用户
    test_client.post(
        "/api/auth/register",
        json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "Password123",
        },
    )
    
    # 尝试向已注册的邮箱发送验证码
    resp = test_client.post(
        "/api/auth/send-verification-code",
        json={"email": "charlie@example.com"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data


def test_register_with_code_flow(test_client):
    # 先发送验证码
    test_client.post(
        "/api/auth/send-verification-code",
        json={"email": "register@example.com"}
    )
    
    # 从服务中获取验证码（在实际测试中，这会打印到控制台）
    from src.server.auth.service import verification_codes
    code = verification_codes["register@example.com"]["code"]
    
    # 使用验证码注册
    resp = test_client.post(
        "/api/auth/register-with-code",
        json={
            "username": "david",
            "email": "register@example.com",
            "password": "Password123",
            "code": code
        }
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "david"
    assert data["email"] == "register@example.com"


def test_register_with_code_wrong_code(test_client):
    # 使用错误的验证码注册
    resp = test_client.post(
        "/api/auth/register-with-code",
        json={
            "username": "eve",
            "email": "eve@example.com",
            "password": "Password123",
            "code": "000000"
        }
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data