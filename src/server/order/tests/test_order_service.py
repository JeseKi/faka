# -*- coding: utf-8 -*-
"""
订单服务层测试
"""

from sqlalchemy.orm import Session

from src.server.order.models import Order
from src.server.order.service import (
    create_order,
    get_order,
    list_pending_orders,
    list_orders,
    complete_order,
    verify_activation_code,
)
from src.server.activation_code.models import ActivationCode, CardCodeStatus
from src.server.order.schemas import OrderStatus
from src.server.channel.models import Channel
from src.server.card.models import Card


def test_create_order(test_db_session: Session):
    """测试创建订单"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道", description="用于测试的渠道")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    activation_code = "TEST-CODE-001"
    channel_id = channel.id
    remarks = "测试订单备注"

    card_name = "测试充值卡"
    order = create_order(
        test_db_session,
        activation_code,
        channel_id,
        OrderStatus.PENDING,
        remarks,
        card_name,
    )

    assert order is not None
    assert order.activation_code == activation_code
    assert order.channel_id == channel_id
    assert order.status == OrderStatus.PENDING
    assert order.remarks == remarks
    assert order.card_name == card_name


def test_get_order(test_db_session: Session):
    """测试获取订单"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道2", description="用于测试的渠道2")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    order = Order(
        activation_code="TEST-CODE-002",
        channel_id=channel.id,
        status=OrderStatus.PENDING,
        user_id=0,
    )
    test_db_session.add(order)
    test_db_session.commit()
    test_db_session.refresh(order)

    # 测试获取存在的订单
    result = get_order(test_db_session, order.id)
    assert result is not None
    assert result.id == order.id
    assert result.activation_code == "TEST-CODE-002"

    # 测试获取不存在的订单
    try:
        get_order(test_db_session, 999999)
        assert False, "应该抛出异常"
    except Exception as e:
        assert "订单不存在" in str(e)


def test_list_pending_orders(test_db_session: Session):
    """测试获取待处理订单列表"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道3", description="用于测试的渠道3")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    order1 = Order(
        activation_code="TEST-CODE-003",
        channel_id=channel.id,
        status=OrderStatus.PENDING,
        user_id=0,
    )
    order2 = Order(
        activation_code="TEST-CODE-004",
        channel_id=channel.id,
        status=OrderStatus.COMPLETED,
        user_id=0,
    )
    order3 = Order(
        activation_code="TEST-CODE-005",
        channel_id=channel.id,
        status=OrderStatus.PENDING,
        user_id=0,
    )

    test_db_session.add_all([order1, order2, order3])
    test_db_session.commit()

    pending_orders = list_pending_orders(test_db_session)

    assert len(pending_orders) == 2
    # 验证返回的订单都是pending状态
    for order in pending_orders:
        assert order.status == OrderStatus.PENDING


def test_list_orders(test_db_session: Session):
    """测试获取订单列表"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道4", description="用于测试的渠道4")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    order1 = Order(
        activation_code="TEST-CODE-006",
        channel_id=channel.id,
        status=OrderStatus.PENDING,
        user_id=0,
    )
    order2 = Order(
        activation_code="TEST-CODE-007",
        channel_id=channel.id,
        status=OrderStatus.COMPLETED,
        user_id=0,
    )
    order3 = Order(
        activation_code="TEST-CODE-008",
        channel_id=channel.id,
        status=OrderStatus.PENDING,
        user_id=0,
    )

    test_db_session.add_all([order1, order2, order3])
    test_db_session.commit()

    # 测试获取所有订单
    all_orders = list_orders(test_db_session)
    assert len(all_orders) == 3

    # 测试按状态过滤
    pending_orders = list_orders(test_db_session, status_filter=OrderStatus.PENDING)
    assert len(pending_orders) == 2
    for order in pending_orders:
        assert order.status == OrderStatus.PENDING


def test_complete_order(test_db_session: Session):
    """测试完成订单"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道5", description="用于测试的渠道5")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    activation_code = ActivationCode(
        card_id=1, code="TEST-CODE-009", status=CardCodeStatus.CONSUMING
    )
    test_db_session.add(activation_code)
    test_db_session.commit()

    order = Order(
        activation_code="TEST-CODE-009",
        channel_id=channel.id,
        status=OrderStatus.PENDING,
        user_id=0,
    )
    test_db_session.add(order)
    test_db_session.commit()
    test_db_session.refresh(order)

    # 完成订单
    completed_order = complete_order(test_db_session, order.id, "测试完成备注")

    assert completed_order is not None
    assert completed_order.status == OrderStatus.COMPLETED
    assert completed_order.remarks == "测试完成备注"
    assert completed_order.completed_at is not None


def test_get_order_with_pricing(test_db_session: Session):
    """测试获取订单时包含正确的 pricing 字段"""
    # 先创建一个渠道
    channel = Channel(
        name="测试渠道_with_pricing", description="用于测试 pricing 的渠道"
    )
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 创建一个商品
    card = Card(
        name="测试充值卡_with_pricing",
        description="用于测试 pricing 的充值卡",
        price=29.99,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建一个卡密
    activation_code = ActivationCode(
        card_id=card.id,
        code="TEST-CODE-PRICING",
        status=CardCodeStatus.AVAILABLE,
    )
    test_db_session.add(activation_code)
    test_db_session.commit()
    test_db_session.refresh(activation_code)

    # 通过 verify_activation_code 创建订单
    order = verify_activation_code(
        test_db_session,
        "TEST-CODE-PRICING",
        channel.id,
        "测试订单备注_with_pricing",
        "自定义充值卡名称_with_pricing",
    )

    # 验证返回的 OrderOut 模型
    assert order is not None
    assert order.activation_code == "TEST-CODE-PRICING"
    assert order.channel_id == channel.id
    assert order.status == OrderStatus.PROCESSING
    assert order.remarks == "测试订单备注_with_pricing"
    assert order.card_name == "自定义充值卡名称_with_pricing"
    assert order.pricing == 29.99  # 验证 pricing 字段

    # 再次通过 get_order 获取订单
    retrieved_order = get_order(test_db_session, order.id)

    # 验证返回的 OrderOut 模型
    assert retrieved_order is not None
    assert retrieved_order.id == order.id
    assert retrieved_order.activation_code == "TEST-CODE-PRICING"
    assert retrieved_order.channel_id == channel.id
    assert retrieved_order.status == OrderStatus.PROCESSING
    assert retrieved_order.remarks == "测试订单备注_with_pricing"
    assert retrieved_order.card_name == "自定义充值卡名称_with_pricing"
    assert retrieved_order.pricing == 29.99  # 验证 pricing 字段


def test_get_order_stats(test_db_session: Session):
    """测试获取订单统计信息"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道6", description="用于测试的渠道6")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    _ = Order(
        activation_code="TEST-CODE-010",
        channel_id=channel.id,
        status=OrderStatus.PENDING,
        user_id=0,
    )
    _ = Order(
        activation_code="TEST-CODE-011",
        channel_id=channel.id,
        status=OrderStatus.COMPLETED,
        user_id=0,
    )
    _ = Order(
        activation_code="TEST-CODE-012",
        channel_id=channel.id,
        status=OrderStatus.PENDING,
        user_id=0,
    )


def test_create_order_with_card_name(test_db_session: Session):
    """测试创建订单时包含充值卡名称"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道7", description="用于测试的渠道7")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    activation_code = "TEST-CODE-013"
    channel_id = channel.id
    card_name = "ChatGPT Plus 充值卡"

    order = create_order(
        test_db_session,
        activation_code,
        channel_id,
        OrderStatus.PENDING,
        None,
        card_name,
    )

    assert order is not None
    assert order.card_name == card_name
    assert order.activation_code == activation_code


def test_create_order_without_card_name(test_db_session: Session):
    """测试创建订单时不包含充值卡名称"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道8", description="用于测试的渠道8")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    activation_code = "TEST-CODE-014"
    channel_id = channel.id

    order = create_order(
        test_db_session, activation_code, channel_id, OrderStatus.PENDING, None, None
    )

    assert order is not None
    assert order.card_name is None
    assert order.activation_code == activation_code


def test_create_order_with_empty_card_name(test_db_session: Session):
    """测试创建订单时包含空的充值卡名称"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道9", description="用于测试的渠道9")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    activation_code = "TEST-CODE-015"
    channel_id = channel.id
    card_name = ""

    order = create_order(
        test_db_session,
        activation_code,
        channel_id,
        OrderStatus.PENDING,
        None,
        card_name,
    )

    assert order is not None
    assert order.card_name == card_name
    assert order.activation_code == activation_code


def test_create_order_with_long_card_name(test_db_session: Session):
    """测试创建订单时包含超长的充值卡名称"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道10", description="用于测试的渠道10")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    activation_code = "TEST-CODE-016"
    channel_id = channel.id
    # 创建一个超过255字符的卡名称（数据库字段限制）
    card_name = "A" * 300

    order = create_order(
        test_db_session,
        activation_code,
        channel_id,
        OrderStatus.PENDING,
        None,
        card_name,
    )

    assert order is not None
    assert order.card_name == card_name
    assert order.activation_code == activation_code
