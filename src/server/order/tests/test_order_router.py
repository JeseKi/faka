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
    codes = create_activation_codes(test_db_session, "测试充值卡", 5)
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
    codes = create_activation_codes(test_db_session, "测试充值卡2", 5)
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
    codes = create_activation_codes(test_db_session, "测试充值卡3", 5)
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
