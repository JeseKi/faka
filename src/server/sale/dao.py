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

    def create(self, activation_code: str, user_email: str, sale_price: float) -> Sale:
        """创建销售记录"""
        sale = Sale(
            activation_code=activation_code,
            user_email=user_email,
            sale_price=sale_price
        )
        self.db_session.add(sale)
        self.db_session.commit()
        self.db_session.refresh(sale)
        return sale

    def get_by_activation_code(self, activation_code: str) -> Sale | None:
        """通过卡密获取销售记录"""
        return self.db_session.query(Sale).filter(
            Sale.activation_code == activation_code
        ).first()

    def get_by_user_email(self, user_email: str) -> list[Sale]:
        """获取用户的购买记录"""
        return self.db_session.query(Sale).filter(
            Sale.user_email == user_email
        ).order_by(Sale.purchased_at.desc()).all()

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Sale]:
        """获取所有销售记录"""
        return self.db_session.query(Sale).order_by(
            Sale.purchased_at.desc()
        ).limit(limit).offset(offset).all()

    def count_all(self) -> int:
        """统计总销售记录数"""
        return self.db_session.query(Sale).count()

    def get_sales_by_date_range(self, start_date, end_date) -> list[Sale]:
        """获取指定日期范围内的销售记录"""
        return self.db_session.query(Sale).filter(
            Sale.purchased_at >= start_date,
            Sale.purchased_at <= end_date
        ).order_by(Sale.purchased_at.desc()).all()

    def get_total_revenue(self) -> float:
        """计算总销售额"""
        from sqlalchemy import func
        result = self.db_session.query(func.sum(Sale.sale_price)).scalar()
        return result or 0.0