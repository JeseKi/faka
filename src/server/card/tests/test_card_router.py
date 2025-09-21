# -*- coding: utf-8 -*-
"""
充值卡模块路由层测试
"""

from http import HTTPStatus


def test_create_card(test_client, test_admin_token):
    """测试创建充值卡"""
    headers = {"Authorization": f"Bearer {test_admin_token}"}

    # 正常创建
    resp = test_client.post(
        "/api/cards",
        json={
            "name": "月度会员",
            "description": "月度会员充值卡",
            "price": 29.99,
            "is_active": True,
            "channel_id": 1
        },
        headers=headers,
    )
    assert resp.status_code == HTTPStatus.CREATED, resp.text
    card = resp.json()
    assert card["name"] == "月度会员"
    assert card["price"] == 29.99
    assert card["channel_id"] == 1

    # 测试重复名称
    resp2 = test_client.post(
        "/api/cards",
        json={
            "name": "月度会员",
            "description": "另一个描述",
            "price": 19.99,
            "is_active": True,
            "channel_id": 1
        },
        headers=headers,
    )
    assert resp2.status_code == HTTPStatus.BAD_REQUEST


def test_list_cards(test_client, test_admin_token):
    """测试列出充值卡"""
    headers = {"Authorization": f"Bearer {test_admin_token}"}

    # 创建测试数据
    test_client.post(
        "/api/cards",
        json={"name": "卡1", "description": "描述1", "price": 10.0, "is_active": True, "channel_id": 1},
        headers=headers,
    )
    test_client.post(
        "/api/cards",
        json={"name": "卡2", "description": "描述2", "price": 20.0, "is_active": False, "channel_id": 1},
        headers=headers,
    )

    # 获取活跃的充值卡
    resp = test_client.get("/api/cards", headers=headers)
    assert resp.status_code == HTTPStatus.OK
    cards = resp.json()
    assert len(cards) == 1  # 只包含刚创建的活跃卡1（卡2是非活跃的）

    # 获取所有充值卡
    resp2 = test_client.get("/api/cards?include_inactive=true", headers=headers)
    assert resp2.status_code == HTTPStatus.OK
    all_cards = resp2.json()
    assert len(all_cards) == 2  # 包含活跃的卡1和非活跃的卡2


def test_get_card(test_client, test_admin_token):
    """测试获取单个充值卡"""
    headers = {"Authorization": f"Bearer {test_admin_token}"}

    # 创建测试数据
    resp = test_client.post(
        "/api/cards",
        json={
            "name": "季度会员",
            "description": "季度会员充值卡",
            "price": 79.99,
            "is_active": True,
            "channel_id": 1
        },
        headers=headers,
    )
    card_id = resp.json()["id"]

    # 获取存在的充值卡
    resp2 = test_client.get(f"/api/cards/{card_id}", headers=headers)
    assert resp2.status_code == HTTPStatus.OK
    card = resp2.json()
    assert card["name"] == "季度会员"

    # 获取不存在的充值卡
    resp3 = test_client.get("/api/cards/999999", headers=headers)
    assert resp3.status_code == HTTPStatus.NOT_FOUND


def test_update_card(test_client, test_admin_token):
    """测试更新充值卡"""
    headers = {"Authorization": f"Bearer {test_admin_token}"}

    # 创建测试数据
    resp = test_client.post(
        "/api/cards",
        json={
            "name": "原名",
            "description": "原描述",
            "price": 50.0,
            "is_active": True,
            "channel_id": 1
        },
        headers=headers,
    )
    card_id = resp.json()["id"]

    # 更新充值卡
    resp2 = test_client.put(
        f"/api/cards/{card_id}", json={"name": "新名", "price": 60.0}, headers=headers
    )
    assert resp2.status_code == HTTPStatus.OK
    updated_card = resp2.json()
    assert updated_card["name"] == "新名"
    assert updated_card["price"] == 60.0
    assert updated_card["description"] == "原描述"  # 未更新的字段保持不变


def test_delete_card(test_client, test_admin_token):
    """测试删除充值卡"""
    headers = {"Authorization": f"Bearer {test_admin_token}"}

    # 创建测试数据
    resp = test_client.post(
        "/api/cards",
        json={
            "name": "待删除",
            "description": "描述",
            "price": 10.0,
            "is_active": True,
            "channel_id": 1
        },
        headers=headers,
    )
    card_id = resp.json()["id"]

    # 删除充值卡
    resp2 = test_client.delete(f"/api/cards/{card_id}", headers=headers)
    assert resp2.status_code == HTTPStatus.OK

    # 验证已删除
    resp3 = test_client.get(f"/api/cards/{card_id}", headers=headers)
    assert resp3.status_code == HTTPStatus.NOT_FOUND


def test_get_card_stock(test_client, test_admin_token):
    """测试获取充值卡库存"""
    headers = {"Authorization": f"Bearer {test_admin_token}"}

    resp = test_client.get("/api/cards/月度会员/stock", headers=headers)
    assert resp.status_code == HTTPStatus.OK
    stock_info = resp.json()
    assert "card_name" in stock_info
    assert "stock" in stock_info
    assert stock_info["stock"] >= 0


def test_unauthorized_access(test_client):
    """测试未授权访问"""
    # 没有 token 的请求
    resp = test_client.post(
        "/api/cards",
        json={"name": "测试", "description": "描述", "price": 10.0, "is_active": True, "channel_id": 1},
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
