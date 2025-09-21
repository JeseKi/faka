# -*- coding: utf-8 -*-
"""
卡密模块服务层

公开接口：
- create_activation_codes(db, card_name, count)
- get_activation_code_by_code(db, code)
- get_available_activation_code(db, card_name)
- set_code_consuming(db, code)
- set_code_consumed(db, code)
- list_activation_codes_by_card(db, card_name, include_used)
- count_activation_codes_by_card(db, card_name, only_unused)
- delete_activation_codes_by_card(db, card_name)
- is_code_available(db, code) -> ActivationCodeCheckResult
- is_code_available_for_user(db, code, user)

内部方法：
- 无

说明：
- 服务层承载业务逻辑，路由层只做参数校验与装配。
"""

from __future__ import annotations

from loguru import logger
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .dao import ActivationCodeDAO
from .models import ActivationCode, CardCodeStatus
from .schemas import ActivationCodeCheckResult
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.card.models import Card


def create_activation_codes(
    db: Session, card_name: str, count: int
) -> list[ActivationCode]:
    """批量创建卡密"""
    dao = ActivationCodeDAO(db)
    return dao.create_batch(card_name, count)


def get_activation_code_by_code(db: Session, code: str) -> ActivationCode | None:
    """通过卡密获取记录"""
    dao = ActivationCodeDAO(db)
    return dao.get_by_code(code)


def get_available_activation_code(db: Session, card_name: str) -> ActivationCode | None:
    """获取指定充值卡的可用卡密"""
    dao = ActivationCodeDAO(db)
    return dao.get_available_by_card_name(card_name)


def mark_activation_code_sold(
    db: Session, activation_code: ActivationCode
) -> ActivationCode:
    """标记卡密为已售出"""
    dao = ActivationCodeDAO(db)
    return dao.mark_as_sold(activation_code)


def set_code_consuming(db: Session, code: str) -> ActivationCode:
    """将卡密状态设置为 consuming"""
    dao = ActivationCodeDAO(db)

    # 获取卡密记录
    activation_code = dao.get_by_code(code)
    if not activation_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡密不存在")

    # 检查状态是否为 available
    if activation_code.status != CardCodeStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="卡密状态不正确"
        )

    # 更新状态为 consuming
    return dao.update_status(activation_code, CardCodeStatus.CONSUMING)


def set_code_consumed(db: Session, code: str) -> ActivationCode:
    """将卡密状态设置为 consumed"""
    dao = ActivationCodeDAO(db)

    # 获取卡密记录
    activation_code = dao.get_by_code(code)
    if not activation_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡密不存在")

    # 检查状态是否为 consuming
    if activation_code.status != CardCodeStatus.CONSUMING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="卡密状态不正确"
        )

    # 更新状态为 consumed
    return dao.update_status(activation_code, CardCodeStatus.CONSUMED)


def list_activation_codes_by_card(
    db: Session, card_name: str, include_used: bool = False
) -> list[ActivationCode]:
    """获取指定充值卡的所有卡密"""
    dao = ActivationCodeDAO(db)
    return dao.list_by_card_name(card_name, include_used)


def count_activation_codes_by_card(
    db: Session, card_name: str, only_unused: bool = True
) -> int:
    """统计指定充值卡的卡密数量"""
    dao = ActivationCodeDAO(db)
    return dao.count_by_card_name(card_name, only_unused)


def delete_activation_codes_by_card(db: Session, card_name: str) -> int:
    """删除指定充值卡的所有卡密"""
    dao = ActivationCodeDAO(db)
    return dao.delete_by_card_name(card_name)


def is_code_available(db: Session, code: str) -> ActivationCodeCheckResult:
    """检查卡密是否可用"""
    dao = ActivationCodeDAO(db)
    logger.info(f"code: {code}")
    activation_code = dao.get_by_code(code)
    logger.info(f"activation_code: {activation_code}")
    if not activation_code:
        logger.info("activation_code not found")
        return ActivationCodeCheckResult(available=False, channel_id=None)

    # 检查卡密状态是否为可用
    available = activation_code.status == CardCodeStatus.AVAILABLE

    # 获取卡密对应的商品和渠道ID
    channel_id = None
    if available:
        card = db.query(Card).filter(Card.name == activation_code.card_name).first()
        if card:
            channel_id = card.channel_id

    return ActivationCodeCheckResult(available=available, channel_id=channel_id)


def is_code_available_for_user(db: Session, code: str, user: User) -> bool:
    """检查卡密是否可用，并且对于 STAFF 用户，检查渠道是否匹配"""
    dao = ActivationCodeDAO(db)
    activation_code = dao.get_by_code(code)
    if not activation_code:
        return False

    # 检查卡密状态是否为可用
    if activation_code.status != CardCodeStatus.AVAILABLE:
        return False

    # 如果用户是 STAFF，需要检查渠道是否匹配
    if user.role == Role.STAFF:
        # 获取卡密对应的商品
        card = db.query(Card).filter(Card.name == activation_code.card_name).first()
        if not card:
            # 如果商品不存在，认为卡密不可用
            return False

        # 检查商品渠道是否与用户渠道一致
        if card.channel_id != user.channel_id:
            return False

    return True
