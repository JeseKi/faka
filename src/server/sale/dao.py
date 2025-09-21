# -*- coding: utf-8 -*-
"""
销售模块 DAO

公开接口：
- `SaleDAO`
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO
from .models import Sale


class SaleDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create(
        self,
        user_id: int,
        card_name: str,
        quantity: int,
        sale_price: float,
        channel_id: int,
        activation_code: str = "",
        user_email: str = "",
    ) -> Sale:
        """创建销售记录"""
        # 这里我们简化处理，只创建一条销售记录，而不是为每个卡密创建一条记录
        # 在实际应用中，可能需要更复杂的逻辑
        sale = Sale(
            user_id=user_id,
            card_name=card_name,
            quantity=quantity,
            sale_price=sale_price,
            channel_id=channel_id,
            activation_code=activation_code,
            user_email=user_email,
        )
        self.db_session.add(sale)
        self.db_session.commit()
        self.db_session.refresh(sale)
        return sale

    def get(self, sale_id: int) -> Sale | None:
        """获取销售记录"""
        return self.db_session.query(Sale).filter(Sale.id == sale_id).first()

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Sale]:
        """获取所有销售记录"""
        return (
            self.db_session.query(Sale)
            .order_by(Sale.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_sales_by_user_id(self, user_id: int) -> list[Sale]:
        """获取指定用户的所有销售记录"""
        return (
            self.db_session.query(Sale)
            .filter(Sale.user_id == user_id)
            .order_by(Sale.created_at.desc())
            .all()
        )
