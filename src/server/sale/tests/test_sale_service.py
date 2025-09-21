# -*- coding: utf-8 -*-
"""
销售模块服务层测试
"""

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.server.sale import service
from src.server.card.models import Card
from src.server.channel.models import Channel
from src.server.activation_code.service import create_activation_codes


def test_create_sale_success(test_db_session: Session):
    """测试成功创建销售记录"""
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
        channel_id=channel.id
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)
    
    # 创建卡密
    _ = create_activation_codes(test_db_session, "测试充值卡", 5)
    
    # 创建销售记录
    sale = service.create_sale(test_db_session, user_id=1, card_name="测试充值卡", quantity=1)
    
    # 验证销售记录已创建
    assert sale.id is not None
    assert sale.user_id == 1
    assert sale.card_name == "测试充值卡"
    assert sale.quantity == 1
    assert sale.sale_price == 10.0
    assert sale.channel_id == channel.id


def test_create_sale_insufficient_stock(test_db_session: Session):
    """测试库存不足时创建销售记录"""
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
        channel_id=channel.id
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)
    
    # 尝试创建超过库存的销售记录，应该抛出HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.create_sale(test_db_session, user_id=1, card_name="测试充值卡", quantity=100)
    
    assert exc_info.value.status_code == 400
    assert "库存不足" in exc_info.value.detail


def test_get_sale_success(test_db_session: Session):
    """测试成功获取销售记录"""
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
        channel_id=channel.id
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)
    
    # 创建卡密
    _ = create_activation_codes(test_db_session, "测试充值卡", 5)
    
    # 创建销售记录
    created_sale = service.create_sale(test_db_session, user_id=1, card_name="测试充值卡", quantity=1)
    
    # 获取销售记录
    retrieved_sale = service.get_sale(test_db_session, created_sale.id)
    
    # 验证销售记录已正确获取
    assert retrieved_sale.id == created_sale.id
    assert retrieved_sale.user_id == 1
    assert retrieved_sale.card_name == "测试充值卡"


def test_get_sale_not_found(test_db_session: Session):
    """测试获取不存在的销售记录"""
    # 尝试获取不存在的销售记录，应该抛出HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.get_sale(test_db_session, 999999)
    
    assert exc_info.value.status_code == 404
    assert "销售记录不存在" in exc_info.value.detail


def test_list_sales(test_db_session: Session):
    """测试获取销售记录列表"""
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
        channel_id=channel.id
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)
    
    # 创建卡密
    _ = create_activation_codes(test_db_session, "测试充值卡", 5)
    
    # 创建多个销售记录
    service.create_sale(test_db_session, user_id=1, card_name="测试充值卡", quantity=1)
    service.create_sale(test_db_session, user_id=2, card_name="测试充值卡", quantity=2)
    
    # 获取销售记录列表
    sales = service.list_sales(test_db_session)
    
    # 验证销售记录列表
    assert len(sales) >= 2


def test_get_sales_by_user_id(test_db_session: Session):
    """测试根据用户ID获取销售记录"""
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
        channel_id=channel.id
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)
    
    # 创建卡密
    _ = create_activation_codes(test_db_session, "测试充值卡", 5)
    
    # 创建属于不同用户的销售记录
    service.create_sale(test_db_session, user_id=1, card_name="测试充值卡", quantity=1)
    service.create_sale(test_db_session, user_id=2, card_name="测试充值卡", quantity=1)
    service.create_sale(test_db_session, user_id=1, card_name="测试充值卡", quantity=2)
    
    # 获取用户1的销售记录
    user_sales = service.get_sales_by_user_id(test_db_session, 1)
    
    # 验证用户1的销售记录
    assert len(user_sales) == 2
    for sale in user_sales:
        assert sale.user_id == 1