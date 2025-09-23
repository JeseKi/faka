# -*- coding: utf-8 -*-
"""
代理商管理服务

公开接口：
- `link_proxy_to_cards`、`unlink_proxy_from_cards`
- `get_proxy_cards`、`get_proxy_card_associations`
- `check_proxy_card_access`、`get_available_cards_for_proxy`
"""

from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session
from loguru import logger

from .models import ProxyCardAssociation
from .schemas import ProxyCardAssociationOut
from src.server.card.models import Card
from src.server.auth.models import User
from src.server.auth.schemas import Role


def link_proxy_to_cards(
    db: Session, proxy_user_id: int, card_ids: List[int]
) -> List[ProxyCardAssociationOut]:
    """为代理商绑定多个充值卡

    Args:
        db: 数据库会话
        proxy_user_id: 代理商用户ID
        card_ids: 要绑定的充值卡ID列表

    Returns:
        List[ProxyCardAssociationOut]: 创建的关联记录列表

    Raises:
        ValueError: 当代理商不存在或角色不是PROXY时
    """
    # 验证代理商用户存在且角色正确
    proxy_user = db.query(User).filter(User.id == proxy_user_id).first()
    if not proxy_user:
        raise ValueError(f"代理商用户ID {proxy_user_id} 不存在")
    if proxy_user.role != Role.PROXY:
        raise ValueError(f"用户 {proxy_user_id} 不是代理商角色")

    # 验证充值卡存在且激活
    existing_cards = db.query(Card).filter(Card.id.in_(card_ids), Card.is_active).all()
    if len(existing_cards) != len(card_ids):
        existing_card_ids = {card.id for card in existing_cards}
        missing_card_ids = set(card_ids) - existing_card_ids
        raise ValueError(f"以下充值卡不存在或未激活: {list(missing_card_ids)}")

    # 创建关联记录
    associations = []
    for card_id in card_ids:
        # 检查是否已存在关联
        existing_association = (
            db.query(ProxyCardAssociation)
            .filter(
                ProxyCardAssociation.proxy_user_id == proxy_user_id,
                ProxyCardAssociation.card_id == card_id,
            )
            .first()
        )

        if existing_association:
            logger.warning(f"代理商 {proxy_user_id} 已绑定充值卡 {card_id}，跳过")
            continue

        association = ProxyCardAssociation(proxy_user_id=proxy_user_id, card_id=card_id)
        db.add(association)
        associations.append(association)

    db.commit()

    # 刷新对象以获取ID
    for association in associations:
        db.refresh(association)

    logger.info(f"代理商 {proxy_user_id} 已绑定 {len(associations)} 个充值卡")
    return [
        ProxyCardAssociationOut.model_validate(association)
        for association in associations
    ]


def unlink_proxy_from_cards(
    db: Session, proxy_user_id: int, card_ids: List[int]
) -> int:
    """为代理商解绑多个充值卡

    Args:
        db: 数据库会话
        proxy_user_id: 代理商用户ID
        card_ids: 要解绑的充值卡ID列表

    Returns:
        int: 实际解绑的关联记录数量

    Raises:
        ValueError: 当代理商不存在或角色不是PROXY时
    """
    # 验证代理商用户存在且角色正确
    proxy_user = db.query(User).filter(User.id == proxy_user_id).first()
    if not proxy_user:
        raise ValueError(f"代理商用户ID {proxy_user_id} 不存在")
    if proxy_user.role != Role.PROXY:
        raise ValueError(f"用户 {proxy_user_id} 不是代理商角色")

    # 删除关联记录
    deleted_count = (
        db.query(ProxyCardAssociation)
        .filter(
            ProxyCardAssociation.proxy_user_id == proxy_user_id,
            ProxyCardAssociation.card_id.in_(card_ids),
        )
        .delete()
    )

    db.commit()

    logger.info(f"代理商 {proxy_user_id} 已解绑 {deleted_count} 个充值卡")
    return deleted_count


def get_proxy_cards(db: Session, proxy_user_id: int) -> List[dict]:
    """获取代理商绑定的充值卡信息

    Args:
        db: 数据库会话
        proxy_user_id: 代理商用户ID

    Returns:
        List[dict]: 充值卡信息列表
    """
    associations = (
        db.query(ProxyCardAssociation)
        .filter(ProxyCardAssociation.proxy_user_id == proxy_user_id)
        .all()
    )

    card_ids = [assoc.card_id for assoc in associations]
    if not card_ids:
        return []

    cards = db.query(Card).filter(Card.id.in_(card_ids), Card.is_active).all()

    return [
        {
            "id": card.id,
            "name": card.name,
            "description": card.description,
            "price": card.price,
            "channel_id": card.channel_id,
            "is_active": card.is_active,
        }
        for card in cards
    ]


def get_proxy_card_associations(
    db: Session, proxy_user_id: int
) -> List[ProxyCardAssociationOut]:
    """获取代理商的所有关联记录

    Args:
        db: 数据库会话
        proxy_user_id: 代理商用户ID

    Returns:
        List[ProxyCardAssociationOut]: 关联记录列表
    """
    associations = (
        db.query(ProxyCardAssociation)
        .filter(ProxyCardAssociation.proxy_user_id == proxy_user_id)
        .all()
    )

    return [ProxyCardAssociationOut.model_validate(assoc) for assoc in associations]


def check_proxy_card_access(db: Session, proxy_user_id: int, card_id: int) -> bool:
    """检查代理商是否有权限访问指定的充值卡

    Args:
        db: 数据库会话
        proxy_user_id: 代理商用户ID
        card_id: 充值卡ID

    Returns:
        bool: 是否有访问权限
    """
    association = (
        db.query(ProxyCardAssociation)
        .filter(
            ProxyCardAssociation.proxy_user_id == proxy_user_id,
            ProxyCardAssociation.card_id == card_id,
        )
        .first()
    )

    return association is not None


def get_available_cards_for_proxy(db: Session, proxy_user_id: int) -> List[dict]:
    """获取代理商可以访问的所有可用充值卡信息

    Args:
        db: 数据库会话
        proxy_user_id: 代理商用户ID

    Returns:
        List[dict]: 可用充值卡信息列表
    """
    # 获取代理商绑定的充值卡ID
    associations = (
        db.query(ProxyCardAssociation)
        .filter(ProxyCardAssociation.proxy_user_id == proxy_user_id)
        .all()
    )

    if not associations:
        return []

    card_ids = [assoc.card_id for assoc in associations]

    # 获取激活的充值卡信息
    cards = db.query(Card).filter(Card.id.in_(card_ids), Card.is_active).all()

    return [
        {
            "id": card.id,
            "name": card.name,
            "description": card.description,
            "price": card.price,
            "channel_id": card.channel_id,
            "is_active": card.is_active,
        }
        for card in cards
    ]


def get_all_proxy_associations(db: Session) -> List[ProxyCardAssociationOut]:
    """获取所有代理商关联记录（管理员权限）

    Args:
        db: 数据库会话

    Returns:
        List[ProxyCardAssociationOut]: 所有关联记录列表
    """
    associations = db.query(ProxyCardAssociation).all()
    return [ProxyCardAssociationOut.model_validate(assoc) for assoc in associations]
