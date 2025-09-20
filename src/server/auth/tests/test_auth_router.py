# -*- coding: utf-8 -*-

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
