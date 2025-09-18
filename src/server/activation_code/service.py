# -*- coding: utf-8 -*-
"""
卡密模块服务层

公开接口：
- create_activation_codes(db, card_name, count)
- get_activation_code_by_code(db, code)
- get_available_activation_code(db, card_name)
- mark_activation_code_used(db, activation_code)
- list_activation_codes_by_card(db, card_name, include_used)
- count_activation_codes_by_card(db, card_name, only_unused)
- delete_activation_codes_by_card(db, card_name)
- verify_and_use_code(db, code)

内部方法：
- 无

说明：
- 服务层承载业务逻辑，路由层只做参数校验与装配。
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .dao import ActivationCodeDAO
from .models import ActivationCode


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


def mark_activation_code_used(
    db: Session, activation_code: ActivationCode
) -> ActivationCode:
    """标记卡密为已使用"""
    dao = ActivationCodeDAO(db)
    return dao.mark_as_used(activation_code)


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


def verify_and_use_code(db: Session, code: str) -> ActivationCode:
    """验证卡密并标记为已使用"""
    dao = ActivationCodeDAO(db)

    # 获取卡密记录
    activation_code = dao.get_by_code(code)
    if not activation_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡密不存在")

    # 检查是否已使用
    if activation_code.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="卡密已被使用"
        )

    # 标记为已使用
    return dao.mark_as_used(activation_code)
