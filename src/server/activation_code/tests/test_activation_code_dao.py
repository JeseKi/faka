# -*- coding: utf-8 -*-
"""
卡密模块DAO层测试
"""

import pytest
from sqlalchemy.orm import Session

from src.server.activation_code.dao import ActivationCodeDAO
from src.server.activation_code.models import CardCodeStatus
from src.server.card.models import Card
from src.server.channel.models import Channel


@pytest.fixture
def setup_test_data(test_db_session: Session):
    """设置测试数据：创建渠道和充值卡"""
    # 创建测试渠道
    channel = Channel(name="测试渠道", description="用于测试的渠道")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)
    
    # 创建测试充值卡
    cards_data = [
        ("月度会员", "月度会员充值卡"),
        ("季度会员", "季度会员充值卡"),
        ("年度会员", "年度会员充值卡"),
        ("状态测试", "状态测试充值卡"),
        ("卡1", "卡1充值卡"),
        ("统计测试", "统计测试充值卡"),
        ("待删除", "待删除充值卡"),
        ("保留", "保留充值卡"),
    ]
    
    cards = []
    for name, description in cards_data:
        card = Card(
            name=name,
            description=description,
            price=10.0,
            is_active=True,
            channel_id=channel.id,
        )
        test_db_session.add(card)
        cards.append(card)
    
    test_db_session.commit()
    for card in cards:
        test_db_session.refresh(card)
    
    return channel, cards


def test_activation_code_dao_create_batch(test_db_session: Session, setup_test_data):
    """测试批量创建卡密"""
    dao = ActivationCodeDAO(test_db_session)

    # 批量创建
    codes = dao.create_batch("月度会员", 3)

    assert len(codes) == 3
    for code in codes:
        assert code.card_name == "月度会员"
        assert code.status == CardCodeStatus.AVAILABLE
        assert code.used_at is None
        assert code.code is not None
        # 加密后的代码长度会更长
        assert len(code.code) > 36


def test_activation_code_dao_get_by_code(test_db_session: Session, setup_test_data):
    """测试通过卡密获取记录"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes = dao.create_batch("季度会员", 1)
    code_value = codes[0].code

    # 获取存在的卡密
    retrieved_code = dao.get_by_code(code_value)
    assert retrieved_code is not None
    assert retrieved_code.code == code_value
    assert retrieved_code.card_name == "季度会员"

    # 获取不存在的卡密
    retrieved_code = dao.get_by_code("non-existent-code")
    assert retrieved_code is None


def test_activation_code_dao_get_available_by_card_name(test_db_session: Session, setup_test_data):
    """测试获取可用卡密"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    _ = dao.create_batch("年度会员", 2)

    # 获取可用卡密
    available_code = dao.get_available_by_card_name("年度会员")
    assert available_code is not None
    assert available_code.card_name == "年度会员"
    assert available_code.status == CardCodeStatus.AVAILABLE

    # 更新状态为 consuming
    dao.update_status(available_code, CardCodeStatus.CONSUMING)

    # 再次获取，应该返回另一个
    another_code = dao.get_available_by_card_name("年度会员")
    assert another_code is not None
    assert another_code.id != available_code.id

    # 更新第二个状态为 consumed
    dao.update_status(another_code, CardCodeStatus.CONSUMED)

    # 应该没有可用卡密了
    no_code = dao.get_available_by_card_name("年度会员")
    assert no_code is None


def test_activation_code_dao_update_status(test_db_session: Session, setup_test_data):
    """测试更新卡密状态"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes = dao.create_batch("状态测试", 1)
    code = codes[0]

    assert code.status == CardCodeStatus.AVAILABLE
    assert code.used_at is None

    # 更新状态为 consuming
    updated_code = dao.update_status(code, CardCodeStatus.CONSUMING)
    assert updated_code.status == CardCodeStatus.CONSUMING
    assert updated_code.used_at is None

    # 更新状态为 consumed
    updated_code = dao.update_status(code, CardCodeStatus.CONSUMED)
    assert updated_code.status == CardCodeStatus.CONSUMED
    assert updated_code.used_at is not None


def test_activation_code_dao_list_by_card_name(test_db_session: Session, setup_test_data):
    """测试列出指定充值卡的卡密"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes1 = dao.create_batch("卡1", 3)

    # 只获取未使用的 (available 状态)
    unused_codes = dao.list_by_card_name("卡1", include_used=False)
    assert len(unused_codes) == 3
    assert all(code.status == CardCodeStatus.AVAILABLE for code in unused_codes)

    # 更新一个为 consuming 状态
    dao.update_status(codes1[0], CardCodeStatus.CONSUMING)

    # 获取所有卡密
    all_codes = dao.list_by_card_name("卡1", include_used=True)
    assert len(all_codes) == 3

    # 只获取未使用的 (available 状态)
    unused_codes = dao.list_by_card_name("卡1", include_used=False)
    assert len(unused_codes) == 2


def test_activation_code_dao_count_by_card_name(test_db_session: Session, setup_test_data):
    """测试统计卡密数量"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes = dao.create_batch("统计测试", 3)

    # 统计未使用的 (available 状态)
    count = dao.count_by_card_name("统计测试", only_unused=True)
    assert count == 3

    # 更新一个为 consuming 状态
    dao.update_status(codes[0], CardCodeStatus.CONSUMING)

    # 再次统计未使用的
    count = dao.count_by_card_name("统计测试", only_unused=True)
    assert count == 2

    # 统计所有
    count = dao.count_by_card_name("统计测试", only_unused=False)
    assert count == 3


def test_activation_code_dao_delete_by_card_name(test_db_session: Session, setup_test_data):
    """测试删除指定充值卡的所有卡密"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    dao.create_batch("待删除", 2)
    dao.create_batch("保留", 1)

    # 删除指定充值卡的卡密
    deleted_count = dao.delete_by_card_name("待删除")
    assert deleted_count == 2

    # 验证已删除
    count = dao.count_by_card_name("待删除", only_unused=False)
    assert count == 0

    # 验证其他卡密未受影响
    count = dao.count_by_card_name("保留", only_unused=False)
    assert count == 1
