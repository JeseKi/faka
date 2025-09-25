# -*- coding: utf-8 -*-
"""
订单路由层测试
"""

import os

from src.server.auth.config import auth_config
from src.server.channel.models import Channel
from src.server.activation_code.service import create_activation_codes

os.environ.setdefault("APP_ENV", "dev")


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


def test_create_order(test_client, test_db_session):
    """测试创建订单"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道", description="用于测试的渠道")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 创建商品
    from src.server.card.models import Card

    card = Card(
        name="测试充值卡",
        description="描述",
        price=10.0,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建卡密
    codes = create_activation_codes(test_db_session, card.id, 5)
    code_value = codes[0].code

    # 创建订单
    order_data = {
        "code": code_value,
        "channel_id": channel.id,
        "remarks": "测试订单备注",
        "card_name": "ChatGPT Plus 充值卡",
    }

    resp = test_client.post("/api/orders/create", json=order_data)
    assert resp.status_code == 201
    order = resp.json()
    assert order["activation_code"] == code_value
    assert order["channel_id"] == channel.id
    assert order["status"] == "processing"  # 默认状态应该是processing
    assert order["card_name"] == "ChatGPT Plus 充值卡"  # 应该使用传入的自定义名称


def test_create_order_with_custom_card_name(test_client, test_db_session):
    """测试创建订单时传入自定义的充值卡名称"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道2", description="用于测试的渠道2")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 创建商品
    from src.server.card.models import Card

    card = Card(
        name="测试充值卡2",
        description="描述2",
        price=15.0,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建卡密
    codes = create_activation_codes(test_db_session, card.id, 5)
    code_value = codes[0].code

    # 创建订单，传入自定义的充值卡名称
    order_data = {
        "code": code_value,
        "channel_id": channel.id,
        "remarks": "测试订单备注2",
        "card_name": "自定义充值卡名称",
    }

    resp = test_client.post("/api/orders/create", json=order_data)
    assert resp.status_code == 201
    order = resp.json()
    assert order["activation_code"] == code_value
    assert order["channel_id"] == channel.id
    assert order["status"] == "processing"
    assert order["card_name"] == "自定义充值卡名称"  # 应该使用传入的自定义名称


def test_create_order_without_card_name(test_client, test_db_session):
    """测试创建订单时不传入充值卡名称"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道3", description="用于测试的渠道3")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 创建商品
    from src.server.card.models import Card

    card = Card(
        name="测试充值卡3",
        description="描述3",
        price=20.0,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建卡密
    codes = create_activation_codes(test_db_session, card.id, 5)
    code_value = codes[0].code

    # 创建订单，不传入充值卡名称
    order_data = {
        "code": code_value,
        "channel_id": channel.id,
        "remarks": "测试订单备注3",
    }

    resp = test_client.post("/api/orders/create", json=order_data)
    assert resp.status_code == 201
    order = resp.json()
    assert order["activation_code"] == code_value
    assert order["channel_id"] == channel.id
    assert order["status"] == "processing"
    assert order["card_name"] == "测试充值卡3"  # 应该使用商品的默认名称


def test_list_orders_with_pricing(test_client, test_db_session):
    """测试获取订单列表时，每个订单都包含正确的 pricing 字段"""
    # 确保管理员用户存在
    from src.server.auth.service import bootstrap_default_admin

    bootstrap_default_admin(test_db_session)

    # 管理员登录（使用test token）
    import os

    os.environ.setdefault("APP_ENV", "test")
    from src.server.auth.config import auth_config

    # 先创建一个渠道
    channel = Channel(
        name="测试渠道_list_with_pricing", description="用于测试订单列表 pricing 的渠道"
    )
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 创建商品
    from src.server.card.models import Card

    card = Card(
        name="测试充值卡_list_with_pricing",
        description="用于测试订单列表 pricing 的充值卡",
        price=49.99,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建卡密和订单
    codes = create_activation_codes(test_db_session, card.id, 2)

    for i, code in enumerate(codes):
        # 创建订单
        order_data = {
            "code": code.code,
            "channel_id": channel.id,
            "remarks": f"测试订单备注_list_with_pricing_{i}",
        }

        resp = test_client.post("/api/orders/create", json=order_data)
        assert resp.status_code == 201

    # 获取订单列表
    orders_resp = test_client.get(
        "/api/orders",
        headers={"Authorization": f"Bearer {auth_config.test_token}"},
    )
    assert orders_resp.status_code == 200
    orders_data = orders_resp.json()
    assert isinstance(orders_data, list)
    # 至少应该有我们刚刚创建的2个订单
    assert len(orders_data) >= 2

    # 验证每个订单都包含 pricing 字段且值正确
    matched_orders = [
        order
        for order in orders_data
        if order["activation_code"] in [code.code for code in codes]
    ]
    assert len(matched_orders) == 2

    for order in matched_orders:
        assert "pricing" in order
        assert order["pricing"] == 49.99


def test_create_order_with_pricing(test_client, test_db_session):
    """测试创建订单时返回的 JSON 数据包含正确的 pricing 字段"""
    # 先创建一个渠道
    channel = Channel(
        name="测试渠道_with_pricing", description="用于测试 pricing 的渠道"
    )
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 创建商品
    from src.server.card.models import Card

    card = Card(
        name="测试充值卡_with_pricing",
        description="用于测试 pricing 的充值卡",
        price=39.99,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建卡密
    codes = create_activation_codes(test_db_session, card.id, 5)
    code_value = codes[0].code

    # 创建订单
    order_data = {
        "code": code_value,
        "channel_id": channel.id,
        "remarks": "测试订单备注_with_pricing",
        "card_name": "自定义充值卡名称_with_pricing",
    }

    resp = test_client.post("/api/orders/create", json=order_data)
    assert resp.status_code == 201
    order = resp.json()
    assert order["activation_code"] == code_value
    assert order["channel_id"] == channel.id
    assert order["status"] == "processing"
    assert order["card_name"] == "自定义充值卡名称_with_pricing"
    assert order["pricing"] == 39.99  # 验证 pricing 字段
