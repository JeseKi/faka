# -*- coding: utf-8 -*-
"""
卡密模块服务层

公开接口：
- create_activation_codes(db, card_id, count)
- get_activation_code_by_code(db, code)
- get_available_activation_code(db, card_id)
- set_code_consuming(db, code)
- set_code_consumed(db, code)
- list_activation_codes_by_card(db, card_id, include_used)
- count_activation_codes_by_card(db, card_id, only_unused)
- delete_activation_codes_by_card(db, card_id)
- is_code_available(db, code) -> ActivationCodeCheckResult
- is_code_available_for_user(db, code, user)

内部方法：
- 无

说明：
- 服务层承载业务逻辑，路由层只做参数校验与装配。
"""

from __future__ import annotations

from loguru import logger
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from .dao import ActivationCodeDAO
from .models import ActivationCode, CardCodeStatus
from .schemas import ActivationCodeCheckResult
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.card.models import Card


def create_activation_codes(
    db: Session, card_id: int, count: int, proxy_user_id: int | None = None
) -> list[ActivationCode]:
    """批量创建卡密"""
    dao = ActivationCodeDAO(db)
    return dao.create_batch(card_id, count, proxy_user_id)


def get_activation_code_by_code(db: Session, code: str) -> ActivationCode | None:
    """通过卡密获取记录"""
    dao = ActivationCodeDAO(db)
    return dao.get_by_code(code)


def get_available_activation_code(db: Session, card_id: int) -> ActivationCode | None:
    """获取指定充值卡的可用卡密"""
    dao = ActivationCodeDAO(db)
    return dao.get_available_by_card_id(card_id)


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
    db: Session, card_id: int, include_used: bool = False
) -> list[ActivationCode]:
    """获取指定充值卡的所有卡密"""
    # 使用 joinedload 预加载关联的 Card 对象，避免 N+1 查询
    query = (
        db.query(ActivationCode)
        .options(joinedload(ActivationCode.card))
        .filter(ActivationCode.card_id == card_id)
    )
    if not include_used:
        query = query.filter(ActivationCode.status == CardCodeStatus.AVAILABLE)
    return query.order_by(ActivationCode.created_at.desc()).all()


def count_activation_codes_by_card(
    db: Session, card_id: int, only_unused: bool = True
) -> int:
    """统计指定充值卡的卡密数量"""
    dao = ActivationCodeDAO(db)
    return dao.count_by_card_id(card_id, only_unused)


def delete_activation_codes_by_card(db: Session, card_id: int) -> int:
    """删除指定充值卡的所有卡密"""
    dao = ActivationCodeDAO(db)
    return dao.delete_by_card_id(card_id)


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
        card = db.query(Card).filter(Card.id == activation_code.card_id).first()
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
        card = db.query(Card).filter(Card.id == activation_code.card_id).first()
        if not card:
            # 如果商品不存在，认为卡密不可用
            return False

        # 检查商品渠道是否与用户渠道一致
        if card.channel_id != user.channel_id:
            return False

    return True


def get_available_activation_codes(
    db: Session, user: User
) -> tuple[list[ActivationCode], int]:
    """根据用户角色获取可用卡密列表

    Args:
        db: 数据库会话
        user: 当前用户

    Returns:
        tuple[list[ActivationCode], int]: (卡密列表, 总数)

    Raises:
        HTTPException: 当用户权限不足时
    """
    from fastapi import HTTPException, status

    # 检查用户权限
    if user.role not in [Role.ADMIN, Role.PROXY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问此接口"
        )

    # 构建查询
    query = db.query(ActivationCode).filter(
        ActivationCode.status == CardCodeStatus.AVAILABLE
    )

    # 根据用户角色和参数筛选
    if user.role == Role.ADMIN:
        pass
    else:
        # 代理商只能查看自己名下的卡密
        query = query.filter(ActivationCode.proxy_user_id == user.id)

    # 获取总数
    total_count = query.count()

    # 获取卡密列表，预加载关联的 Card 对象
    codes = (
        query.options(joinedload(ActivationCode.card))
        .order_by(ActivationCode.created_at.desc())
        .all()
    )

    return codes, total_count


def mark_codes_as_exported(db: Session, code_ids: list[int], user: User) -> int:
    """批量标记卡密为已导出

    Args:
        db: 数据库会话
        code_ids: 要导出的卡密ID列表
        user: 当前用户

    Returns:
        int: 成功导出的卡密数量

    Raises:
        HTTPException: 当用户权限不足时
    """
    from fastapi import HTTPException, status

    # 检查用户权限
    if user.role not in [Role.ADMIN, Role.PROXY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问此接口"
        )

    # 调用 DAO 层执行批量更新
    dao = ActivationCodeDAO(db)

    # 如果是代理商，只允许操作自己代理的卡密
    if user.role == Role.PROXY:
        return dao.mark_as_exported(code_ids, user_id=user.id)
    else:
        # 管理员可以操作所有卡密
        return dao.mark_as_exported(code_ids)
