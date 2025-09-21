# -*- coding: utf-8 -*-
"""
卡密模块测试 fixtures
"""

import pytest
from sqlalchemy.orm import Session

from src.server.card.models import Card
from src.server.channel.models import Channel


@pytest.fixture
def test_channel(test_db_session: Session) -> Channel:
    """创建测试渠道"""
    channel = Channel(name="测试渠道", description="用于测试的渠道")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)
    return channel


@pytest.fixture
def test_card(test_db_session: Session, test_channel: Channel) -> Card:
    """创建测试充值卡"""
    card = Card(
        name="测试充值卡",
        description="用于测试的充值卡",
        price=10.0,
        is_active=True,
        channel_id=test_channel.id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)
    return card


def create_test_card(test_db_session: Session, name: str, channel_id: int) -> Card:
    """创建指定名称的测试充值卡"""
    card = Card(
        name=name,
        description=f"{name}充值卡",
        price=10.0,
        is_active=True,
        channel_id=channel_id,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)
    return card
