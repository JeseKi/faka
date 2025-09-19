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
    get_order_stats,
    get_orders_by_user_id,
)
from src.server.activation_code.models import ActivationCode


def test_create_order(test_db_session: Session):
    """测试创建订单"""
    activation_code = "TEST-CODE-001"
    user_id = 1
    remarks = "测试订单备注"

    order = create_order(test_db_session, activation_code, user_id, "pending", remarks)

    assert order is not None
    assert order.activation_code == activation_code
    assert order.user_id == user_id
    assert order.status == "pending"
    assert order.remarks == remarks


def test_get_order(test_db_session: Session):
    """测试获取订单"""
    # 准备测试数据
    order = Order(activation_code="TEST-CODE-002", user_id=1, status="pending")
    test_db_session.add(order)
    test_db_session.commit()
    test_db_session.refresh(order)

    # 测试获取存在的订单
    result = get_order(test_db_session, order.id)
    assert result is not None
    assert result.id == order.id
    assert result.activation_code == "TEST-CODE-002"

    # 测试获取不存在的订单
    result = get_order(test_db_session, 999999)
    assert result is None


def test_list_pending_orders(test_db_session: Session):
    """测试获取待处理订单列表"""
    # 准备测试数据
    order1 = Order(activation_code="TEST-CODE-003", user_id=1, status="pending")
    order2 = Order(activation_code="TEST-CODE-004", user_id=2, status="completed")
    order3 = Order(activation_code="TEST-CODE-005", user_id=3, status="pending")

    test_db_session.add_all([order1, order2, order3])
    test_db_session.commit()

    pending_orders = list_pending_orders(test_db_session)

    assert len(pending_orders) == 2
    # 验证返回的订单都是pending状态
    for order in pending_orders:
        assert order.status == "pending"


def test_list_orders(test_db_session: Session):
    """测试获取订单列表"""
    # 准备测试数据
    order1 = Order(activation_code="TEST-CODE-006", user_id=1, status="pending")
    order2 = Order(activation_code="TEST-CODE-007", user_id=2, status="completed")
    order3 = Order(activation_code="TEST-CODE-008", user_id=3, status="pending")

    test_db_session.add_all([order1, order2, order3])
    test_db_session.commit()

    # 测试获取所有订单
    all_orders = list_orders(test_db_session)
    assert len(all_orders) == 3

    # 测试按状态过滤
    pending_orders = list_orders(test_db_session, status_filter="pending")
    assert len(pending_orders) == 2
    for order in pending_orders:
        assert order.status == "pending"


def test_complete_order(test_db_session: Session):
    """测试完成订单"""
    # 准备测试数据
    activation_code = ActivationCode(code="TEST-CODE-009", status="used")
    test_db_session.add(activation_code)
    test_db_session.commit()

    order = Order(activation_code="TEST-CODE-009", user_id=1, status="pending")
    test_db_session.add(order)
    test_db_session.commit()
    test_db_session.refresh(order)

    # 完成订单
    completed_order = complete_order(test_db_session, order.id, "测试完成备注")

    assert completed_order is not None
    assert completed_order.status == "completed"
    assert completed_order.remarks == "测试完成备注"
    assert completed_order.completed_at is not None


def test_get_order_stats(test_db_session: Session):
    """测试获取订单统计信息"""
    # 准备测试数据
    order1 = Order(activation_code="TEST-CODE-010", user_id=1, status="pending")
    order2 = Order(activation_code="TEST-CODE-011", user_id=2, status="completed")
    order3 = Order(activation_code="TEST-CODE-012", user_id=3, status="pending")

    test_db_session.add_all([order1, order2, order3])
    test_db_session.commit()

    stats = get_order_stats(test_db_session)

    assert "total_orders" in stats
    assert "pending_orders" in stats
    assert "completed_orders" in stats
    assert stats["total_orders"] == 3
    assert stats["pending_orders"] == 2
    assert stats["completed_orders"] == 1


def test_get_orders_by_user_id(test_db_session: Session):
    """测试获取指定用户的所有订单"""
    user_id = 1
    # 准备测试数据
    order1 = Order(activation_code="TEST-CODE-013", user_id=user_id, status="pending")
    order2 = Order(activation_code="TEST-CODE-014", user_id=user_id, status="completed")
    order3 = Order(
        activation_code="TEST-CODE-015", user_id=2, status="pending"
    )  # 不同用户

    test_db_session.add_all([order1, order2, order3])
    test_db_session.commit()

    user_orders = get_orders_by_user_id(test_db_session, user_id)

    assert len(user_orders) == 2
    for order in user_orders:
        assert order.user_id == user_id
