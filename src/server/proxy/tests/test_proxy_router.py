# -*- coding: utf-8 -*-
"""代理商管理路由层测试"""

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from src.server.proxy.models import ProxyCardAssociation
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.card.models import Card


def create_user_helper(
    test_db_session: Session,
    username: str,
    email: str,
    password: str,
    role: Role = Role.USER,
) -> User:
    """辅助函数：直接在数据库中创建用户"""
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


def get_auth_token(test_client, username: str, password: str) -> str:
    """辅助函数：获取用户认证token"""
    login_resp = test_client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert login_resp.status_code == 200, f"登录失败: {login_resp.text}"
    return login_resp.json()["access_token"]


def test_link_proxy_to_cards_success(test_client, test_db_session: Session):
    """测试成功为代理商绑定充值卡"""
    # 准备测试数据
    proxy_user = User(
        username="proxy_test", email="proxy_test@example.com", role=Role.PROXY
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card = Card(
        name="Test Card",
        description="Test Description",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 测试绑定充值卡
    response = test_client.post(
        "/api/proxy/link",
        json={"proxy_user_id": proxy_user.id, "card_ids": [card.id]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 注意：这个测试需要实际的认证中间件支持
    # 这里只是展示测试结构，实际测试时需要设置正确的认证

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["proxy_user_id"] == proxy_user.id
    assert data[0]["card_id"] == card.id


def test_unlink_proxy_from_cards_success(
    test_client: TestClient, test_db_session: Session
):
    """测试成功为代理商解绑充值卡"""
    # 准备测试数据
    proxy_user = create_user_helper(
        test_db_session,
        "proxy_test2",
        "proxy_test2@example.com",
        "password123",
        Role.PROXY,
    )

    card = Card(
        name="Test Card",
        description="Test Description",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 先创建关联
    association = ProxyCardAssociation(proxy_user_id=proxy_user.id, card_id=card.id)
    test_db_session.add(association)
    test_db_session.commit()

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin2", "admin2@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin2", "admin123")

    # 测试解绑充值卡
    response = test_client.post(
        "/api/proxy/unlink",
        json={"proxy_user_id": proxy_user.id, "card_ids": [card.id]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "成功解绑 1 个充值卡" in data["message"]


def test_get_proxy_cards_success(test_client: TestClient, test_db_session: Session):
    """测试成功获取代理商绑定的充值卡列表"""
    # 准备测试数据
    proxy_user = create_user_helper(
        test_db_session,
        "proxy_test3",
        "proxy_test3@example.com",
        "password123",
        Role.PROXY,
    )

    card = Card(
        name="Test Card",
        description="Test Description",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建关联
    association = ProxyCardAssociation(proxy_user_id=proxy_user.id, card_id=card.id)
    test_db_session.add(association)
    test_db_session.commit()

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin3", "admin3@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin3", "admin123")

    # 测试获取代理商绑定的充值卡
    response = test_client.get(
        f"/api/proxy/{proxy_user.id}/cards",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["proxy_user_id"] == proxy_user.id
    assert len(data["cards"]) == 1
    assert data["cards"][0]["name"] == "Test Card"
    assert data["total_count"] == 1


def test_get_all_proxy_associations_success(
    test_client: TestClient, test_db_session: Session
):
    """测试成功获取所有代理商关联记录"""
    # 准备测试数据
    proxy_user = create_user_helper(
        test_db_session,
        "proxy_test4",
        "proxy_test4@example.com",
        "password123",
        Role.PROXY,
    )

    card = Card(
        name="Test Card",
        description="Test Description",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建关联
    association = ProxyCardAssociation(proxy_user_id=proxy_user.id, card_id=card.id)
    test_db_session.add(association)
    test_db_session.commit()

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin4", "admin4@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin4", "admin123")

    # 测试获取所有关联记录
    response = test_client.get(
        "/api/proxy/associations", headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["proxy_user_id"] == proxy_user.id
    assert data[0]["card_id"] == card.id


def test_proxy_router_unauthorized(test_client: TestClient):
    """测试未授权访问代理商管理接口"""
    # 测试访问需要管理员权限的接口
    response = test_client.post(
        "/api/proxy/link", json={"proxy_user_id": 1, "card_ids": [1]}
    )

    # 应该返回401或403
    assert response.status_code in [401, 403]


def test_link_proxy_to_cards_invalid_data(
    test_client: TestClient, test_db_session: Session
):
    """测试绑定充值卡时传入无效数据"""
    # 准备测试数据
    proxy_user = create_user_helper(
        test_db_session,
        "proxy_test5",
        "proxy_test5@example.com",
        "password123",
        Role.PROXY,
    )

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin5", "admin5@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin5", "admin123")

    # 测试绑定不存在的充值卡
    response = test_client.post(
        "/api/proxy/link",
        json={
            "proxy_user_id": proxy_user.id,
            "card_ids": [999],  # 不存在的卡ID
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 应该返回400错误
    assert response.status_code == 400
    data = response.json()
    assert "不存在" in data["detail"]


def test_unlink_proxy_from_cards_invalid_data(
    test_client: TestClient, test_db_session: Session
):
    """测试解绑充值卡时传入无效数据"""
    # 准备测试数据
    proxy_user = create_user_helper(
        test_db_session,
        "proxy_test6",
        "proxy_test6@example.com",
        "password123",
        Role.PROXY,
    )

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin6", "admin6@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin6", "admin123")

    # 测试解绑不存在的充值卡
    response = test_client.post(
        "/api/proxy/unlink",
        json={
            "proxy_user_id": proxy_user.id,
            "card_ids": [999],  # 不存在的卡ID
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 应该返回200，但实际解绑数量为0
    assert response.status_code == 200
    data = response.json()
    assert "成功解绑 0 个充值卡" in data["message"]
