# -*- coding: utf-8 -*-
"""代理商管理服务层测试"""

from sqlalchemy.orm import Session

from src.server.proxy.models import ProxyCardAssociation
from src.server.proxy.service import (
    link_proxy_to_cards,
    unlink_proxy_from_cards,
    get_proxy_cards,
    get_proxy_card_associations,
    check_proxy_card_access,
    get_available_cards_for_proxy,
    get_all_proxy_associations,
)
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.card.models import Card


def test_link_proxy_to_cards(test_db_session: Session):
    """测试为代理商绑定充值卡"""
    # 准备测试数据
    proxy_user = User(username="proxy1", email="proxy1@example.com", role=Role.PROXY)
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card1 = Card(
        name="Test Card 1",
        description="Test Description 1",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    card2 = Card(
        name="Test Card 2",
        description="Test Description 2",
        price=20.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add_all([card1, card2])
    test_db_session.commit()
    test_db_session.refresh(card1)
    test_db_session.refresh(card2)

    # 测试绑定充值卡
    associations = link_proxy_to_cards(
        test_db_session, proxy_user.id, [card1.id, card2.id]
    )

    assert len(associations) == 2
    assert associations[0].proxy_user_id == proxy_user.id
    assert associations[0].card_id == card1.id
    assert associations[1].proxy_user_id == proxy_user.id
    assert associations[1].card_id == card2.id

    # 验证数据库中的关联记录
    db_associations = (
        test_db_session.query(ProxyCardAssociation)
        .filter(ProxyCardAssociation.proxy_user_id == proxy_user.id)
        .all()
    )
    assert len(db_associations) == 2


def test_link_proxy_to_cards_duplicate(test_db_session: Session):
    """测试重复绑定充值卡"""
    # 准备测试数据
    proxy_user = User(username="proxy2", email="proxy2@example.com", role=Role.PROXY)
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card = Card(
        name="Test Card",
        description="Test Description",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 第一次绑定
    associations1 = link_proxy_to_cards(test_db_session, proxy_user.id, [card.id])
    assert len(associations1) == 1

    # 第二次绑定相同卡（应该被跳过）
    associations2 = link_proxy_to_cards(test_db_session, proxy_user.id, [card.id])
    assert len(associations2) == 0


def test_link_proxy_to_cards_invalid_proxy(test_db_session: Session):
    """测试绑定不存在的代理商"""
    # 测试绑定不存在的代理商
    try:
        link_proxy_to_cards(test_db_session, 999, [1])
        assert False, "应该抛出异常"
    except ValueError as e:
        assert "代理商用户ID 999 不存在" in str(e)


def test_link_proxy_to_cards_invalid_role(test_db_session: Session):
    """测试绑定非代理商角色的用户"""
    # 准备测试数据
    normal_user = User(username="normal", email="normal@example.com", role=Role.USER)
    normal_user.set_password("password123")
    test_db_session.add(normal_user)
    test_db_session.commit()
    test_db_session.refresh(normal_user)

    # 测试绑定非代理商用户
    try:
        link_proxy_to_cards(test_db_session, normal_user.id, [1])
        assert False, "应该抛出异常"
    except ValueError as e:
        assert "不是代理商角色" in str(e)


def test_unlink_proxy_from_cards(test_db_session: Session):
    """测试为代理商解绑充值卡"""
    # 准备测试数据
    proxy_user = User(username="proxy3", email="proxy3@example.com", role=Role.PROXY)
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card = Card(
        name="Test Card",
        description="Test Description",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 先绑定
    link_proxy_to_cards(test_db_session, proxy_user.id, [card.id])

    # 再解绑
    deleted_count = unlink_proxy_from_cards(test_db_session, proxy_user.id, [card.id])
    assert deleted_count == 1

    # 验证数据库中的关联记录已被删除
    db_associations = (
        test_db_session.query(ProxyCardAssociation)
        .filter(ProxyCardAssociation.proxy_user_id == proxy_user.id)
        .all()
    )
    assert len(db_associations) == 0


def test_get_proxy_cards(test_db_session: Session):
    """测试获取代理商绑定的充值卡"""
    # 准备测试数据
    proxy_user = User(username="proxy4", email="proxy4@example.com", role=Role.PROXY)
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card1 = Card(
        name="Test Card 1",
        description="Test Description 1",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    card2 = Card(
        name="Test Card 2",
        description="Test Description 2",
        price=20.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add_all([card1, card2])
    test_db_session.commit()
    test_db_session.refresh(card1)
    test_db_session.refresh(card2)

    # 绑定充值卡
    link_proxy_to_cards(test_db_session, proxy_user.id, [card1.id, card2.id])

    # 获取代理商绑定的充值卡
    cards = get_proxy_cards(test_db_session, proxy_user.id)

    assert len(cards) == 2
    card_names = [card["name"] for card in cards]
    assert "Test Card 1" in card_names
    assert "Test Card 2" in card_names


def test_get_proxy_card_associations(test_db_session: Session):
    """测试获取代理商的所有关联记录"""
    # 准备测试数据
    proxy_user = User(username="proxy5", email="proxy5@example.com", role=Role.PROXY)
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card = Card(
        name="Test Card",
        description="Test Description",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add(card)
    test_db_session.commit()
    test_db_session.refresh(card)

    # 绑定充值卡
    link_proxy_to_cards(test_db_session, proxy_user.id, [card.id])

    # 获取关联记录
    associations = get_proxy_card_associations(test_db_session, proxy_user.id)

    assert len(associations) == 1
    assert associations[0].proxy_user_id == proxy_user.id
    assert associations[0].card_id == card.id


def test_check_proxy_card_access(test_db_session: Session):
    """测试检查代理商是否有权限访问充值卡"""
    # 准备测试数据
    proxy_user = User(username="proxy6", email="proxy6@example.com", role=Role.PROXY)
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card1 = Card(
        name="Test Card 1",
        description="Test Description 1",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    card2 = Card(
        name="Test Card 2",
        description="Test Description 2",
        price=20.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add_all([card1, card2])
    test_db_session.commit()
    test_db_session.refresh(card1)
    test_db_session.refresh(card2)

    # 绑定一个充值卡
    link_proxy_to_cards(test_db_session, proxy_user.id, [card1.id])

    # 测试有权限访问的充值卡
    assert check_proxy_card_access(test_db_session, proxy_user.id, card1.id) is True

    # 测试无权限访问的充值卡
    assert check_proxy_card_access(test_db_session, proxy_user.id, card2.id) is False


def test_get_available_cards_for_proxy(test_db_session: Session):
    """测试获取代理商可以访问的可用充值卡"""
    # 准备测试数据
    proxy_user = User(username="proxy7", email="proxy7@example.com", role=Role.PROXY)
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    card1 = Card(
        name="Test Card 1",
        description="Test Description 1",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    card2 = Card(
        name="Test Card 2",
        description="Test Description 2",
        price=20.0,
        channel_id=1,
        is_active=False,  # 这个卡未激活
    )
    test_db_session.add_all([card1, card2])
    test_db_session.commit()
    test_db_session.refresh(card1)
    test_db_session.refresh(card2)

    # 绑定充值卡
    link_proxy_to_cards(test_db_session, proxy_user.id, [card1.id])  # 只绑定激活的卡

    # 获取可用充值卡
    available_cards = get_available_cards_for_proxy(test_db_session, proxy_user.id)

    # 应该只返回激活的充值卡
    assert len(available_cards) == 1
    assert available_cards[0]["name"] == "Test Card 1"
    assert available_cards[0]["is_active"] is True


def test_get_all_proxy_associations(test_db_session: Session):
    """测试获取所有代理商关联记录（管理员权限）"""
    # 准备测试数据
    proxy_user1 = User(username="proxy8", email="proxy8@example.com", role=Role.PROXY)
    proxy_user1.set_password("password123")
    proxy_user2 = User(username="proxy9", email="proxy9@example.com", role=Role.PROXY)
    proxy_user2.set_password("password123")
    test_db_session.add_all([proxy_user1, proxy_user2])
    test_db_session.commit()
    test_db_session.refresh(proxy_user1)
    test_db_session.refresh(proxy_user2)

    card1 = Card(
        name="Test Card 1",
        description="Test Description 1",
        price=10.0,
        channel_id=1,
        is_active=True,
    )
    card2 = Card(
        name="Test Card 2",
        description="Test Description 2",
        price=20.0,
        channel_id=1,
        is_active=True,
    )
    test_db_session.add_all([card1, card2])
    test_db_session.commit()
    test_db_session.refresh(card1)
    test_db_session.refresh(card2)

    # 绑定充值卡
    link_proxy_to_cards(test_db_session, proxy_user1.id, [card1.id])
    link_proxy_to_cards(test_db_session, proxy_user2.id, [card2.id])

    # 获取所有关联记录
    all_associations = get_all_proxy_associations(test_db_session)

    assert len(all_associations) == 2
    proxy_ids = [assoc.proxy_user_id for assoc in all_associations]
    card_ids = [assoc.card_id for assoc in all_associations]
    assert proxy_user1.id in proxy_ids
    assert proxy_user2.id in proxy_ids
    assert card1.id in card_ids
    assert card2.id in card_ids
