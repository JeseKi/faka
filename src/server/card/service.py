# -*- coding: utf-8 -*-
"""
充值卡模块服务层

公开接口：
- create_card(db, card_in)
- get_card(db, card_id)
- get_card_by_name(db, name)
- list_cards(db, include_inactive)
- update_card(db, card, card_in)
- delete_card(db, card)
- list_cards_by_channel(db, channel_id, include_inactive)

内部方法：
- 无

说明：
- 服务层承载业务逻辑，路由层只做参数校验与装配。
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .dao import CardDAO
from .models import Card
from .schemas import CardCreate, CardUpdate


def create_card(db: Session, card_in: CardCreate) -> Card:
    dao = CardDAO(db)
    try:
        return dao.create(card_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def get_card(db: Session, card_id: int) -> Card:
    dao = CardDAO(db)
    card = dao.get(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="充值卡不存在"
        )
    return card


def get_card_by_name(db: Session, name: str) -> Card:
    dao = CardDAO(db)
    card = dao.get_by_name(name)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="充值卡不存在"
        )
    return card


def list_cards(db: Session, include_inactive: bool = False) -> list[Card]:
    dao = CardDAO(db)
    return dao.list_all(include_inactive)


def list_cards_by_channel(
    db: Session, channel_id: int, include_inactive: bool = False
) -> list[Card]:
    """根据渠道ID获取充值卡列表"""
    dao = CardDAO(db)
    return dao.list_by_channel(channel_id, include_inactive)


def update_card(db: Session, card: Card, card_in: CardUpdate) -> Card:
    dao = CardDAO(db)
    try:
        return dao.update(card, card_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def delete_card(db: Session, card: Card) -> None:
    dao = CardDAO(db)
    dao.delete(card)


def get_card_stock(db: Session, card_id: int) -> int:
    """获取充值卡库存数量"""
    dao = CardDAO(db)
    return dao.get_stock_count_by_id(card_id)
