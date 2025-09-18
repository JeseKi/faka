# -*- coding: utf-8 -*-
"""
充值卡模块服务层测试
"""

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.server.card.models import Card
from src.server.card.service import (
    create_card,
    get_card,
    get_card_by_name,
    list_cards,
    update_card,
    delete_card,
    get_card_stock,
)


def test_create_card(test_db_session: Session):
    """测试创建充值卡"""
    # 正常创建
    card = create_card(test_db_session, "月度会员", "月度会员充值卡", 29.99, True)

    assert card is not None
    assert card.name == "月度会员"
    assert card.description == "月度会员充值卡"
    assert card.price == 29.99
    assert card.is_active

    # 测试重复名称
    with pytest.raises(HTTPException) as exc_info:
        create_card(test_db_session, "月度会员", "另一个描述", 19.99, True)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "充值卡名称已存在"


def test_get_card(test_db_session: Session):
    """测试获取充值卡"""
    # 准备测试数据
    card = Card(
        name="季度会员", description="季度会员充值卡", price=79.99, is_active=True
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 获取存在的充值卡
    retrieved_card = get_card(test_db_session, card.id)
    assert retrieved_card is not None
    assert retrieved_card.id == card.id
    assert retrieved_card.name == "季度会员"

    # 获取不存在的充值卡
    with pytest.raises(HTTPException) as exc_info:
        get_card(test_db_session, 999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "充值卡不存在"


def test_get_card_by_name(test_db_session: Session):
    """测试通过名称获取充值卡"""
    # 准备测试数据
    card = Card(
        name="年度会员", description="年度会员充值卡", price=299.99, is_active=True
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 获取存在的充值卡
    retrieved_card = get_card_by_name(test_db_session, "年度会员")
    assert retrieved_card is not None
    assert retrieved_card.name == "年度会员"

    # 获取不存在的充值卡
    with pytest.raises(HTTPException) as exc_info:
        get_card_by_name(test_db_session, "不存在的卡")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "充值卡不存在"


def test_list_cards(test_db_session: Session):
    """测试列出充值卡"""
    # 准备测试数据
    card1 = Card(name="卡1", description="描述1", price=10.0, is_active=True)
    card2 = Card(name="卡2", description="描述2", price=20.0, is_active=False)
    card3 = Card(name="卡3", description="描述3", price=30.0, is_active=True)
    test_db_session.add_all([card1, card2, card3])
    test_db_session.commit()

    # 只获取活跃的充值卡
    active_cards = list_cards(test_db_session, include_inactive=False)
    assert len(active_cards) == 2
    assert all(card.is_active for card in active_cards)

    # 获取所有充值卡
    all_cards = list_cards(test_db_session, include_inactive=True)
    assert len(all_cards) == 3


def test_update_card(test_db_session: Session):
    """测试更新充值卡"""
    # 准备测试数据
    card = Card(name="原名", description="原描述", price=50.0, is_active=True)
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 更新部分字段
    updated_card = update_card(test_db_session, card, name="新名", price=60.0)
    assert updated_card.name == "新名"
    assert updated_card.price == 60.0
    assert updated_card.description == "原描述"  # 未更新的字段保持不变

    # 测试更新为重复名称
    card2 = Card(name="另一个卡", description="描述", price=40.0, is_active=True)
    test_db_session.add(card2)
    test_db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        update_card(test_db_session, card2, name="新名")  # 新名已被 card 使用

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "充值卡名称已存在"


def test_delete_card(test_db_session: Session):
    """测试删除充值卡"""
    # 准备测试数据
    card = Card(name="待删除", description="描述", price=10.0, is_active=True)
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 删除充值卡
    delete_card(test_db_session, card)

    # 验证已删除
    deleted_card = test_db_session.query(Card).filter(Card.id == card.id).first()
    assert deleted_card is None


def test_get_card_stock(test_db_session: Session):
    """测试获取充值卡库存"""
    # 由于库存计算依赖 activation_code 表，这里先测试基本功能
    stock = get_card_stock(test_db_session, "不存在的卡")
    assert stock == 0
