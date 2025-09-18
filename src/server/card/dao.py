# -*- coding: utf-8 -*-
"""
充值卡模块 DAO

公开接口：
- `CardDAO`
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.server.dao.dao_base import BaseDAO
from .models import Card


class CardDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create(self, name: str, description: str, price: float, is_active: bool = True) -> Card:
        exists = self.db_session.query(Card).filter(Card.name == name).first()
        if exists:
            raise ValueError("充值卡名称已存在")
        card = Card(name=name, description=description, price=price, is_active=is_active)
        self.db_session.add(card)
        self.db_session.commit()
        self.db_session.refresh(card)
        return card

    def get(self, card_id: int) -> Card | None:
        return self.db_session.query(Card).filter(Card.id == card_id).first()

    def get_by_name(self, name: str) -> Card | None:
        return self.db_session.query(Card).filter(Card.name == name).first()

    def list_all(self, include_inactive: bool = False) -> list[Card]:
        query = self.db_session.query(Card)
        if not include_inactive:
            query = query.filter(Card.is_active == True)
        return query.order_by(Card.id).all()

    def update(self, card: Card, name: str | None = None, description: str | None = None,
               price: float | None = None, is_active: bool | None = None) -> Card:
        if name is not None:
            # 检查名称是否已被其他卡使用
            existing = self.db_session.query(Card).filter(Card.name == name, Card.id != card.id).first()
            if existing:
                raise ValueError("充值卡名称已存在")
            card.name = name
        if description is not None:
            card.description = description
        if price is not None:
            card.price = price
        if is_active is not None:
            card.is_active = is_active

        self.db_session.commit()
        self.db_session.refresh(card)
        return card

    def delete(self, card: Card) -> None:
        self.db_session.delete(card)
        self.db_session.commit()

    def get_stock_count(self, card_name: str) -> int:
        """获取指定充值卡的库存数量（通过关联的未使用的卡密计算）"""
        from src.server.activation_code.models import ActivationCode
        return self.db_session.query(ActivationCode).filter(
            ActivationCode.card_name == card_name,
            ActivationCode.is_used == False
        ).count()