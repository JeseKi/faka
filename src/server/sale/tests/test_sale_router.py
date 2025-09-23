# -*- coding: utf-8 -*-
"""
销售模块路由测试
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.sale.models import Sale
from src.server.card.models import Card
from src.server.channel.models import Channel
from src.server.activation_code.service import create_activation_codes


@pytest.fixture
def admin_user(test_db_session: Session) -> User:
    """创建管理员用户"""
    user = User(
        username="test_admin",
        email="test_admin@example.com",
        name="测试管理员",
        role=Role.ADMIN,
    )
    user.set_password("test_password")
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(test_client: TestClient, admin_user: User) -> str:
    """获取管理员token"""
    response = test_client.post(
        "/api/auth/login", json={"username": "test_admin", "password": "test_password"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_list_sales_success(
    test_client: TestClient, admin_token: str, test_db_session: Session
):
    """测试成功获取销售记录列表"""
    # 创建渠道
    channel = Channel(name="测试渠道", description="测试渠道描述")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 创建充值卡
    card = Card(
        name="测试充值卡",
        description="测试充值卡描述",
        price=10.0,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建卡密
    codes = create_activation_codes(test_db_session, card.id, 5)

    # 创建销售记录
    sale = Sale(
        user_id=1,
        card_name="测试充值卡",
        quantity=1,
        sale_price=10.0,
        channel_id=channel.id,
        activation_code=codes[0].code,
        user_email="test@example.com",
    )
    test_db_session.add(sale)
    test_db_session.commit()

    # 获取销售记录列表
    response = test_client.get(
        "/api/sales", headers={"Authorization": f"Bearer {admin_token}"}
    )

    # 验证响应
    assert response.status_code == 200
    sales = response.json()
    assert len(sales) >= 1
    assert sales[0]["card_name"] == "测试充值卡"


def test_list_sales_unauthorized(test_client: TestClient):
    """测试未授权获取销售记录列表"""
    response = test_client.get("/api/sales")
    assert response.status_code == 401


def test_get_sales_stats(test_client: TestClient, admin_token: str):
    """测试获取销售统计信息"""
    response = test_client.get(
        "/api/sales/stats", headers={"Authorization": f"Bearer {admin_token}"}
    )

    # 验证响应
    assert response.status_code == 200
    stats = response.json()
    assert "message" in stats
    assert stats["message"] == "销售统计功能尚未实现"


def test_get_user_sales(test_client: TestClient, admin_token: str):
    """测试获取用户销售记录"""
    response = test_client.get(
        "/api/sales/user/test@example.com",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 验证响应
    assert response.status_code == 200
    sales = response.json()
    assert isinstance(sales, list)
