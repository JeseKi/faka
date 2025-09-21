# -*- coding: utf-8 -*-
"""
充值卡模块DAO层测试
"""

import pytest
from sqlalchemy.orm import Session

from src.server.card.dao import CardDAO
from src.server.card.models import Card
from src.server.card.schemas import CardCreate, CardUpdate
from src.server.channel.models import Channel


def test_card_dao_create(test_db_session: Session):
    """测试创建充值卡"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道", description="用于测试的渠道")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    dao = CardDAO(test_db_session)

    # 正常创建
    card_in = CardCreate(
        name="月度会员",
        description="月度会员充值卡",
        price=29.99,
        is_active=True,
        channel_id=channel.id,
    )
    card = dao.create(card_in)

    assert card is not None
    assert card.name == "月度会员"
    assert card.description == "月度会员充值卡"
    assert card.price == 29.99
    assert card.is_active
    assert card.channel_id == channel.id

    # 测试重复名称
    with pytest.raises(ValueError) as exc_info:
        card_in2 = CardCreate(
            name="月度会员",
            description="另一个描述",
            price=19.99,
            is_active=True,
            channel_id=channel.id,
        )
        dao.create(card_in2)

    assert str(exc_info.value) == "充值卡名称已存在"


def test_card_dao_get(test_db_session: Session):
    """测试获取充值卡"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道2", description="用于测试的渠道2")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    card = Card(
        name="季度会员",
        description="季度会员充值卡",
        price=79.99,
        is_active=True,
        channel_id=channel.id,
    )
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
    # 先创建一个渠道
    channel = Channel(name="测试渠道3", description="用于测试的渠道3")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    card = Card(
        name="年度会员",
        description="年度会员充值卡",
        price=299.99,
        is_active=True,
        channel_id=channel.id,
    )
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
    # 先创建一个渠道
    channel = Channel(name="测试渠道4", description="用于测试的渠道4")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    card1 = Card(
        name="卡1",
        description="描述1",
        price=10.0,
        is_active=True,
        channel_id=channel.id,
    )
    card2 = Card(
        name="卡2",
        description="描述2",
        price=20.0,
        is_active=False,
        channel_id=channel.id,
    )
    card3 = Card(
        name="卡3",
        description="描述3",
        price=30.0,
        is_active=True,
        channel_id=channel.id,
    )
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
    # 先创建两个渠道
    channel1 = Channel(name="测试渠道5", description="用于测试的渠道5")
    channel2 = Channel(name="测试渠道6", description="用于测试的渠道6")
    test_db_session.add_all([channel1, channel2])
    test_db_session.commit()
    test_db_session.refresh(channel1)
    test_db_session.refresh(channel2)

    # 准备测试数据
    card = Card(
        name="原名",
        description="原描述",
        price=50.0,
        is_active=True,
        channel_id=channel1.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    dao = CardDAO(test_db_session)

    # 更新部分字段
    card_update = CardUpdate(name="新名", price=60.0)
    updated_card = dao.update(card, card_update)
    assert updated_card.name == "新名"
    assert updated_card.price == 60.0
    assert updated_card.description == "原描述"  # 未更新的字段保持不变

    # 测试更新为重复名称
    card2 = Card(
        name="另一个卡",
        description="描述",
        price=40.0,
        is_active=True,
        channel_id=channel1.id,
    )
    test_db_session.add(card2)
    test_db_session.commit()

    with pytest.raises(ValueError) as exc_info:
        card_update2 = CardUpdate(name="新名")  # 新名已被 card 使用
        dao.update(card2, card_update2)

    assert str(exc_info.value) == "充值卡名称已存在"


def test_card_dao_delete(test_db_session: Session):
    """测试删除充值卡"""
    # 先创建一个渠道
    channel = Channel(name="测试渠道7", description="用于测试的渠道7")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    card = Card(
        name="待删除",
        description="描述",
        price=10.0,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    dao = CardDAO(test_db_session)

    # 删除充值卡
    dao.delete(card)

    # 验证已删除
    deleted_card = test_db_session.query(Card).filter(Card.id == card.id).first()
    assert deleted_card is None


def test_get_stock_count(test_db_session: Session):
    """测试获取充值卡库存数量"""
    from src.server.activation_code.dao import ActivationCodeDAO
    from src.server.card.dao import CardDAO
    from src.server.activation_code.models import CardCodeStatus

    # 先创建一个渠道
    channel = Channel(name="测试渠道8", description="用于测试的渠道8")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)

    # 准备测试数据
    card = Card(
        name="库存测试卡",
        description="描述",
        price=10.0,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 创建卡密数据
    activation_dao = ActivationCodeDAO(test_db_session)
    codes = activation_dao.create_batch("库存测试卡", 5)

    # 测试库存数量
    card_dao = CardDAO(test_db_session)
    stock_count = card_dao.get_stock_count("库存测试卡")
    assert stock_count == 5

    # 更新一个卡密状态为 consuming
    activation_dao.update_status(codes[0], CardCodeStatus.CONSUMING)

    # 再次测试库存数量
    stock_count = card_dao.get_stock_count("库存测试卡")
    assert stock_count == 4

    # 更新一个卡密状态为 consumed
    activation_dao.update_status(codes[1], CardCodeStatus.CONSUMED)

    # 再次测试库存数量
    stock_count = card_dao.get_stock_count("库存测试卡")
    assert stock_count == 3
