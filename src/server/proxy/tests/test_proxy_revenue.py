# -*- coding: utf-8 -*-
"""代理商销售额计算测试"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from src.server.proxy.service import calculate_proxy_revenue
from src.server.proxy.schemas import RevenueQueryParams
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.card.models import Card
from src.server.activation_code.models import ActivationCode, CardCodeStatus
from src.server.sale.models import Sale


def test_calculate_proxy_revenue_self(test_db_session: Session):
    """测试代理商查看自己的销售额"""
    # 准备测试数据
    proxy_user = User(
        username="proxy_revenue",
        email="proxy_revenue@example.com",
        role=Role.PROXY,
        name="测试代理商",
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    # 创建充值卡
    card = Card(
        name="Revenue Test Card",
        description="Test Description",
        price=50.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 先绑定代理商与充值卡
    from src.server.proxy.service import link_proxy_to_cards

    link_proxy_to_cards(test_db_session, proxy_user.id, [card.id])

    # 创建已消费的卡密
    consumed_code = ActivationCode(
        card_id=card.id,
        code="TEST123456",
        status=CardCodeStatus.CONSUMED,
        proxy_user_id=proxy_user.id,
        used_at=datetime.now(timezone.utc),
    )
    test_db_session.add(consumed_code)
    test_db_session.commit()
    test_db_session.refresh(consumed_code)

    # 创建销售记录
    sale = Sale(
        user_id=123,
        activation_code=consumed_code.code,
        sale_price=50.0,
        purchased_at=datetime.now(timezone.utc),
        card_name=card.name,
        quantity=1,
        channel_id=1,
    )
    test_db_session.add(sale)
    test_db_session.commit()

    # 测试计算销售额
    query_params = RevenueQueryParams(
        start_date=None, end_date=None, proxy_id=None, username=None, name=None
    )
    result = calculate_proxy_revenue(test_db_session, proxy_user, query_params)

    assert result.proxy_user_id == proxy_user.id
    assert result.proxy_username == proxy_user.username
    assert result.proxy_name == proxy_user.name
    assert result.total_revenue == 50.0
    assert result.consumed_count == 1
    assert result.query_time_range == "全部时间"


def test_calculate_proxy_revenue_with_time_filter(test_db_session: Session):
    """测试代理商查看指定时间范围内的销售额"""
    # 准备测试数据
    proxy_user = User(
        username="proxy_time", email="proxy_time@example.com", role=Role.PROXY
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card = Card(
        name="Time Test Card",
        description="Test Description",
        price=30.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 先绑定代理商与充值卡
    from src.server.proxy.service import link_proxy_to_cards

    link_proxy_to_cards(test_db_session, proxy_user.id, [card.id])

    # 创建两个已消费的卡密
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(days=5)
    new_time = now - timedelta(days=1)

    old_consumed_code = ActivationCode(
        card_id=card.id,
        code="OLD123456",
        status=CardCodeStatus.CONSUMED,
        proxy_user_id=proxy_user.id,
        used_at=old_time,
    )
    new_consumed_code = ActivationCode(
        card_id=card.id,
        code="NEW123456",
        status=CardCodeStatus.CONSUMED,
        proxy_user_id=proxy_user.id,
        used_at=new_time,
    )
    test_db_session.add_all([old_consumed_code, new_consumed_code])
    test_db_session.commit()

    # 创建对应的销售记录
    old_sale = Sale(
        user_id=123,
        activation_code=old_consumed_code.code,
        sale_price=30.0,
        purchased_at=old_time,
        card_name=card.name,
        quantity=1,
        channel_id=1,
    )
    new_sale = Sale(
        user_id=124,
        activation_code=new_consumed_code.code,
        sale_price=30.0,
        purchased_at=new_time,
        card_name=card.name,
        quantity=1,
        channel_id=1,
    )
    test_db_session.add_all([old_sale, new_sale])
    test_db_session.commit()

    # 测试查询最近2天的销售额
    start_date = now - timedelta(days=2)
    query_params = RevenueQueryParams(
        start_date=start_date, end_date=None, proxy_id=None, username=None, name=None
    )
    result = calculate_proxy_revenue(test_db_session, proxy_user, query_params)

    assert result.total_revenue == 30.0  # 只有最近的销售记录
    assert result.consumed_count == 1
    assert "从" in result.query_time_range and "开始" in result.query_time_range


def test_calculate_proxy_revenue_admin_query(test_db_session: Session):
    """测试管理员查询特定代理商的销售额"""
    # 准备测试数据
    admin_user = User(
        username="admin_revenue", email="admin_revenue@example.com", role=Role.ADMIN
    )
    admin_user.set_password("password123")
    test_db_session.add(admin_user)
    test_db_session.commit()
    test_db_session.refresh(admin_user)

    proxy_user = User(
        username="proxy_admin",
        email="proxy_admin@example.com",
        role=Role.PROXY,
        name="被查询代理商",
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card = Card(
        name="Admin Test Card",
        description="Test Description",
        price=100.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 先绑定代理商与充值卡
    from src.server.proxy.service import link_proxy_to_cards

    link_proxy_to_cards(test_db_session, proxy_user.id, [card.id])

    # 创建已消费的卡密
    consumed_code = ActivationCode(
        card_id=card.id,
        code="ADMIN123456",
        status=CardCodeStatus.CONSUMED,
        proxy_user_id=proxy_user.id,
        used_at=datetime.now(timezone.utc),
    )
    test_db_session.add(consumed_code)
    test_db_session.commit()

    # 创建销售记录
    sale = Sale(
        user_id=125,
        activation_code=consumed_code.code,
        sale_price=100.0,
        purchased_at=datetime.now(timezone.utc),
        card_name=card.name,
        quantity=1,
        channel_id=1,
    )
    test_db_session.add(sale)
    test_db_session.commit()

    # 管理员通过用户名查询
    query_params = RevenueQueryParams(
        start_date=None,
        end_date=None,
        proxy_id=None,
        username=proxy_user.username,
        name=None,
    )
    result = calculate_proxy_revenue(test_db_session, admin_user, query_params)

    assert result.proxy_user_id == proxy_user.id
    assert result.proxy_username == proxy_user.username
    assert result.proxy_name == proxy_user.name
    assert result.total_revenue == 100.0
    assert result.consumed_count == 1


def test_calculate_proxy_revenue_no_consumed_codes(test_db_session: Session):
    """测试代理商没有已消费卡密的情况"""
    # 准备测试数据
    proxy_user = User(
        username="proxy_no_sales", email="proxy_no_sales@example.com", role=Role.PROXY
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    # 创建充值卡但不创建卡密
    card = Card(
        name="No Sales Card",
        description="Test Description",
        price=25.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()

    # 测试计算销售额
    query_params = RevenueQueryParams(
        start_date=None, end_date=None, proxy_id=None, username=None, name=None
    )
    result = calculate_proxy_revenue(test_db_session, proxy_user, query_params)

    assert result.total_revenue == 0.0
    assert result.consumed_count == 0
    assert result.query_time_range == "无绑定卡密"


def test_calculate_proxy_revenue_invalid_permission(test_db_session: Session):
    """测试非代理商和管理员用户查询销售额"""
    # 准备测试数据
    normal_user = User(
        username="normal_user", email="normal_user@example.com", role=Role.USER
    )
    normal_user.set_password("password123")
    test_db_session.add(normal_user)
    test_db_session.commit()

    query_params = RevenueQueryParams(
        start_date=None, end_date=None, proxy_id=None, username=None, name=None
    )

    # 应该抛出异常
    with pytest.raises(ValueError, match="只有代理商和管理员才能查询销售额"):
        calculate_proxy_revenue(test_db_session, normal_user, query_params)


def test_calculate_proxy_revenue_admin_invalid_proxy(test_db_session: Session):
    """测试管理员查询不存在的代理商"""
    # 准备测试数据
    admin_user = User(
        username="admin_invalid", email="admin_invalid@example.com", role=Role.ADMIN
    )
    admin_user.set_password("password123")
    test_db_session.add(admin_user)
    test_db_session.commit()

    query_params = RevenueQueryParams(
        start_date=None,
        end_date=None,
        proxy_id=None,
        username="nonexistent_proxy",
        name=None,
    )

    # 应该抛出异常
    with pytest.raises(ValueError, match="指定的代理商不存在"):
        calculate_proxy_revenue(test_db_session, admin_user, query_params)


def test_calculate_proxy_revenue_admin_non_proxy_user(test_db_session: Session):
    """测试管理员查询非代理商用户"""
    # 准备测试数据
    admin_user = User(
        username="admin_non_proxy", email="admin_non_proxy@example.com", role=Role.ADMIN
    )
    admin_user.set_password("password123")
    test_db_session.add(admin_user)
    test_db_session.commit()

    normal_user = User(
        username="normal_for_admin",
        email="normal_for_admin@example.com",
        role=Role.USER,
    )
    normal_user.set_password("password123")
    test_db_session.add(normal_user)
    test_db_session.commit()

    query_params = RevenueQueryParams(
        start_date=None,
        end_date=None,
        proxy_id=None,
        username=normal_user.username,
        name=None,
    )

    # 应该抛出异常
    with pytest.raises(ValueError, match="指定的用户不是代理商"):
        calculate_proxy_revenue(test_db_session, admin_user, query_params)
