# -*- coding: utf-8 -*-
"""
充值卡模块 DAO

公开接口：
- `CardDAO`
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO
from .models import Card
from .schemas import CardCreate, CardUpdate


class CardDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create(self, card_in: CardCreate) -> Card:
        """创建充值卡"""
        # 检查名称是否已存在
        existing = self.db_session.query(Card).filter(Card.name == card_in.name).first()
        if existing:
            raise ValueError("充值卡名称已存在")

        card = Card(
            name=card_in.name,
            description=card_in.description,
            price=card_in.price,
            is_active=card_in.is_active,
            channel_id=card_in.channel_id,
        )
        self.db_session.add(card)
        self.db_session.commit()
        self.db_session.refresh(card)
        return card

    def get(self, card_id: int) -> Card | None:
        """获取充值卡"""
        return self.db_session.query(Card).filter(Card.id == card_id).first()

    def get_by_name(self, name: str) -> Card | None:
        """通过名称获取充值卡"""
        return self.db_session.query(Card).filter(Card.name == name).first()

    def list_all(self, include_inactive: bool = False) -> list[Card]:
        """获取所有充值卡"""
        query = self.db_session.query(Card)
        if not include_inactive:
            query = query.filter(Card.is_active.is_(True))
        return query.order_by(Card.id.desc()).all()

    def list_by_channel(self, channel_id: int, include_inactive: bool = False) -> list[Card]:
        """根据渠道ID获取充值卡"""
        query = self.db_session.query(Card).filter(Card.channel_id == channel_id)
        if not include_inactive:
            query = query.filter(Card.is_active.is_(True))
        return query.order_by(Card.id.desc()).all()

    def update(self, card: Card, card_in: CardUpdate) -> Card:
        """更新充值卡"""
        # 如果更新了名称，检查是否与其他充值卡冲突
        if card_in.name and card_in.name != card.name:
            existing = (
                self.db_session.query(Card)
                .filter(Card.name == card_in.name, Card.id != card.id)
                .first()
            )
            if existing:
                raise ValueError("充值卡名称已存在")

        update_data = card_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(card, field, value)

        self.db_session.commit()
        self.db_session.refresh(card)
        return card

    def delete(self, card: Card) -> None:
        """删除充值卡"""
        self.db_session.delete(card)
        self.db_session.commit()

    def get_stock_count(self, card_name: str) -> int:
        """获取充值卡库存数量"""
        from src.server.activation_code.service import count_activation_codes_by_card

        return count_activation_codes_by_card(self.db_session, card_name, only_unused=True)
