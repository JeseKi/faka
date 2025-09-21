# -*- coding: utf-8 -*-
"""
卡密消费流程测试
"""

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.server.activation_code.service import (
    create_activation_codes,
    set_code_consuming,
    set_code_consumed,
)
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
    card = Card(
        name="消费测试",
        description="消费测试充值卡",
        price=10.0,
        is_active=True,
        channel_id=channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)
    
    return channel, card


def test_consuming_api_success(test_db_session: Session, setup_test_data):
    """测试 consuming API 成功场景"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "消费测试", 1)
    code_value = codes[0].code

    # 调用 consuming API
    consuming_code = set_code_consuming(test_db_session, code_value)

    # 验证状态已更新为 consuming
    assert consuming_code.status == CardCodeStatus.CONSUMING
    assert consuming_code.used_at is None


def test_consuming_api_invalid_status(test_db_session: Session, setup_test_data):
    """测试对非 available 状态的卡密调用 consuming 接口失败"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "消费测试", 1)
    code_value = codes[0].code

    # 先将卡密状态设置为 consuming
    dao = ActivationCodeDAO(test_db_session)
    code_obj = dao.get_by_code(code_value)
    assert code_obj
    dao.update_status(code_obj, CardCodeStatus.CONSUMING)

    # 尝试再次调用 consuming API，应该失败
    with pytest.raises(HTTPException) as exc_info:
        set_code_consuming(test_db_session, code_value)

    assert exc_info.value.status_code == 400
    assert "状态不正确" in exc_info.value.detail


def test_consumed_api_success(test_db_session: Session, setup_test_data):
    """测试 consumed API 成功场景"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "消费测试", 1)
    code_value = codes[0].code

    # 先将卡密状态设置为 consuming
    _ = set_code_consuming(test_db_session, code_value)

    # 调用 consumed API
    consumed_code = set_code_consumed(test_db_session, code_value)

    # 验证状态已更新为 consumed
    assert consumed_code.status == CardCodeStatus.CONSUMED
    assert consumed_code.used_at is not None


def test_consumed_api_invalid_status(test_db_session: Session, setup_test_data):
    """测试对非 consuming 状态的卡密调用 consumed 接口失败"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "消费测试", 1)
    code_value = codes[0].code

    # 直接调用 consumed API，应该失败（因为状态是 available）
    with pytest.raises(HTTPException) as exc_info:
        set_code_consumed(test_db_session, code_value)

    assert exc_info.value.status_code == 400
    assert "状态不正确" in exc_info.value.detail
