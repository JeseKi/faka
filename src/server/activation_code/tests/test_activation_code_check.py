# -*- coding: utf-8 -*-
"""
卡密检查可用性 API 测试
"""

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from src.server.activation_code.service import create_activation_codes


def test_check_code_availability_success(
    test_client: TestClient, test_db_session: Session, test_admin_token: str
):
    """测试成功检查卡密是否可用"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "可用性测试", 1)
    code_value = codes[0].code

    # 直接调用服务函数检查卡密是否可用
    from src.server.activation_code.service import is_code_available

    is_available = is_code_available(test_db_session, code_value)
    assert is_available is True

    # 调用 API 检查卡密是否可用
    response = test_client.get(
        "/api/activation-codes/check",
        params={"code": code_value},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    print(f"Response data: {data}")  # 添加调试信息
    assert data["available"] is True


def test_check_code_availability_not_found(
    test_client: TestClient, test_admin_token: str
):
    """测试检查不存在的卡密"""
    # 调用 API 检查不存在的卡密
    response = test_client.get(
        "/api/activation-codes/check",
        params={"code": "non-existent-code"},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False


def test_check_code_availability_consumed(
    test_client: TestClient, test_db_session: Session, test_admin_token: str
):
    """测试检查已消费的卡密"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "可用性测试", 1)
    code_value = codes[0].code

    # 将卡密状态设置为 consuming
    response = test_client.post(
        "/api/activation-codes/consuming", json={"code": code_value}
    )
    assert response.status_code == 200

    # 再将卡密状态设置为 consumed
    response = test_client.post(
        "/api/activation-codes/consumed", json={"code": code_value}
    )
    assert response.status_code == 200

    # 调用 API 检查卡密是否可用
    response = test_client.get(
        "/api/activation-codes/check",
        params={"code": code_value},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False


def test_check_code_availability_consuming(
    test_client: TestClient, test_db_session: Session, test_admin_token: str
):
    """测试检查正在消费的卡密"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "可用性测试", 1)
    code_value = codes[0].code

    # 将卡密状态设置为 consuming
    response = test_client.post(
        "/api/activation-codes/consuming", json={"code": code_value}
    )
    assert response.status_code == 200

    # 调用 API 检查卡密是否可用
    response = test_client.get(
        "/api/activation-codes/check",
        params={"code": code_value},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False
