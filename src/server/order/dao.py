# -*- coding: utf-8 -*-
"""
订单模块 DAO

公开接口：
- `OrderDAO`
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO
from .models import Order


class OrderDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create(
        self,
        activation_code: str,
        user_id: int,
        status: str = "pending",
        remarks: str | None = None,
    ) -> Order:
        """创建订单"""
        order = Order(
            activation_code=activation_code,
            user_id=user_id,
            status=status,
            remarks=remarks,
        )
        self.db_session.add(order)
        self.db_session.commit()
        self.db_session.refresh(order)
        return order

    def get(self, order_id: int) -> Order | None:
        """获取订单"""
        return self.db_session.query(Order).filter(Order.id == order_id).first()

    def get_by_activation_code(self, activation_code: str) -> Order | None:
        """通过卡密获取订单"""
        return (
            self.db_session.query(Order)
            .filter(Order.activation_code == activation_code)
            .first()
        )

    def get_orders_by_user_id(self, user_id: int) -> list[Order]:
        """获取指定用户的所有订单"""
        return (
            self.db_session.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def list_pending(self) -> list[Order]:
        """获取所有待处理订单"""
        return (
            self.db_session.query(Order)
            .filter(Order.status == "pending")
            .order_by(Order.created_at.asc())
            .all()
        )

    def list_all(
        self, status_filter: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[Order]:
        """获取所有订单"""
        query = self.db_session.query(Order)

        if status_filter:
            query = query.filter(Order.status == status_filter)

        return query.order_by(Order.created_at.desc()).limit(limit).offset(offset).all()

    def update_status(
        self, order: Order, status: str, remarks: str | None = None
    ) -> Order:
        """更新订单状态"""
        order.status = status
        if status == "completed":
            order.completed_at = datetime.now(timezone.utc)
        if remarks is not None:
            order.remarks = remarks

        self.db_session.commit()
        self.db_session.refresh(order)
        return order

    def count_by_status(self, status: str) -> int:
        """统计指定状态的订单数量"""
        return self.db_session.query(Order).filter(Order.status == status).count()

    def get_recent_orders(self, days: int = 7) -> list[Order]:
        """获取最近几天的订单"""
        from datetime import timedelta

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        return (
            self.db_session.query(Order)
            .filter(Order.created_at >= cutoff_date)
            .order_by(Order.created_at.desc())
            .all()
        )
