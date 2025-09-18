# -*- coding: utf-8 -*-
"""
充值卡模块DAO层测试
"""

import pytest
from sqlalchemy.orm import Session

from src.server.card.dao import CardDAO
from src.server.card.models import Card


def test_card_dao_create(test_db_session: Session):
    """测试创建充值卡"""
    dao = CardDAO(test_db_session)

    # 正常创建
    card = dao.create("月度会员", "月度会员充值卡", 29.99, True)

    assert card is not None
    assert card.name == "月度会员"
    assert card.description == "月度会员充值卡"
    assert card.price == 29.99
    assert card.is_active

    # 测试重复名称
    with pytest.raises(ValueError) as exc_info:
        dao.create("月度会员", "另一个描述", 19.99, True)

    assert str(exc_info.value) == "充值卡名称已存在"


def test_card_dao_get(test_db_session: Session):
    """测试获取充值卡"""
    # 准备测试数据
    card = Card(name="季度会员", description="季度会员充值卡", price=79.99, is_active=True)
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    dao = CardDAO(test_db_session)

    # 获取存在的充值卡
    retrieved_card = dao.get(card.id)
    assert retrieved_card is not None
    assert retrieved_card.id == card.id
    assert retrieved_card.name == "季度会员"

    # 获取不存在的充值卡
    retrieved_card = dao.get(999999)
    assert retrieved_card is None


def test_card_dao_get_by_name(test_db_session: Session):
    """测试通过名称获取充值卡"""
    # 准备测试数据
    card = Card(name="年度会员", description="年度会员充值卡", price=299.99, is_active=True)
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    dao = CardDAO(test_db_session)

    # 获取存在的充值卡
    retrieved_card = dao.get_by_name("年度会员")
    assert retrieved_card is not None
    assert retrieved_card.name == "年度会员"

    # 获取不存在的充值卡
    retrieved_card = dao.get_by_name("不存在的卡")
    assert retrieved_card is None


def test_card_dao_list_all(test_db_session: Session):
    """测试列出所有充值卡"""
    # 准备测试数据
    card1 = Card(name="卡1", description="描述1", price=10.0, is_active=True)
    card2 = Card(name="卡2", description="描述2", price=20.0, is_active=False)
    card3 = Card(name="卡3", description="描述3", price=30.0, is_active=True)
    test_db_session.add_all([card1, card2, card3])
    test_db_session.commit()

    dao = CardDAO(test_db_session)

    # 只获取活跃的充值卡
    active_cards = dao.list_all(include_inactive=False)
    assert len(active_cards) == 2
    assert all(card.is_active for card in active_cards)

    # 获取所有充值卡
    all_cards = dao.list_all(include_inactive=True)
    assert len(all_cards) == 3


def test_card_dao_update(test_db_session: Session):
    """测试更新充值卡"""
    # 准备测试数据
    card = Card(name="原名", description="原描述", price=50.0, is_active=True)
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    dao = CardDAO(test_db_session)

    # 更新部分字段
    updated_card = dao.update(card, name="新名", price=60.0)
    assert updated_card.name == "新名"
    assert updated_card.price == 60.0
    assert updated_card.description == "原描述"  # 未更新的字段保持不变

    # 测试更新为重复名称
    card2 = Card(name="另一个卡", description="描述", price=40.0, is_active=True)
    test_db_session.add(card2)
    test_db_session.commit()

    with pytest.raises(ValueError) as exc_info:
        dao.update(card2, name="新名")  # 新名已被 card 使用

    assert str(exc_info.value) == "充值卡名称已存在"


def test_card_dao_delete(test_db_session: Session):
    """测试删除充值卡"""
    # 准备测试数据
    card = Card(name="待删除", description="描述", price=10.0, is_active=True)
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    dao = CardDAO(test_db_session)

    # 删除充值卡
    dao.delete(card)

    # 验证已删除
    deleted_card = test_db_session.query(Card).filter(Card.id == card.id).first()
    assert deleted_card is None