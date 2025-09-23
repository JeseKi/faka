# -*- coding: utf-8 -*-
"""
卡密检查可用性 API 测试
"""

import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from src.server.activation_code.service import create_activation_codes
from src.server.card.models import Card
from src.server.channel.models import Channel


@pytest.fixture
def setup_test_data(test_db_session: Session):
    """设置测试数据：创建渠道和充值卡"""
    # 创建测试渠道
    channel = Channel(name="测试渠道", description="用于测试的渠道")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 创建测试充值卡
    card = Card(
        name="可用性测试",
        description="可用性测试充值卡",
        price=10.0,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    return channel, card


def test_check_code_availability_success(
    test_client: TestClient,
    test_db_session: Session,
    test_admin_token: str,
    setup_test_data,
):
    """测试成功检查卡密是否可用"""
    _, card = setup_test_data
    card_id = card.id  # "可用性测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
    code_value = codes[0].code

    # 直接调用服务函数检查卡密是否可用
    from src.server.activation_code.service import is_code_available

    result = is_code_available(test_db_session, code_value)
    assert result.available is True

    # 调用 API 检查卡密是否可用
    response = test_client.get(
        "/api/activation-codes/check",
        params={"code": code_value},
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True


def test_check_code_availability_not_found(test_client: TestClient, setup_test_data):
    """测试检查不存在的卡密"""
    # 调用 API 检查不存在的卡密
    response = test_client.get(
        "/api/activation-codes/check",
        params={"code": "non-existent-code"},
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False


def test_check_code_availability_consumed(
    test_client: TestClient, test_db_session: Session, setup_test_data
):
    """测试检查已消费的卡密"""
    _, card = setup_test_data
    card_id = card.id  # "可用性测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
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
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False


def test_check_code_availability_consuming(
    test_client: TestClient, test_db_session: Session, setup_test_data
):
    """测试检查正在消费的卡密"""
    _, card = setup_test_data
    card_id = card.id  # "可用性测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
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
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False
