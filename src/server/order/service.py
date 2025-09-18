# -*- coding: utf-8 -*-
"""
订单模块服务层

公开接口：
- verify_activation_code(db, code)
- create_order(db, activation_code, status, remarks)
- get_order(db, order_id)
- list_pending_orders(db)
- list_orders(db, status_filter, limit, offset)
- complete_order(db, order_id, remarks)
- get_order_stats(db)

内部方法：
- 无

说明：
- 服务层承载业务逻辑，路由层只做参数校验与装配。
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .dao import OrderDAO
from .models import Order


def verify_activation_code(db: Session, code: str) -> Order:
    """验证卡密并创建订单"""
    from src.server.activation_code.service import verify_and_use_code

    # 验证并使用卡密
    activation_code = verify_and_use_code(db, code)

    # 创建订单
    dao = OrderDAO(db)
    order = dao.create(activation_code.code, status="pending")

    return order


def create_order(db: Session, activation_code: str, status: str = "pending", remarks: str | None = None) -> Order:
    """创建订单"""
    dao = OrderDAO(db)
    return dao.create(activation_code, status, remarks)


def get_order(db: Session, order_id: int) -> Order:
    """获取订单"""
    dao = OrderDAO(db)
    order = dao.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return order


def list_pending_orders(db: Session) -> list[Order]:
    """获取所有待处理订单"""
    dao = OrderDAO(db)
    return dao.list_pending()


def list_orders(db: Session, status_filter: str | None = None, limit: int = 100, offset: int = 0) -> list[Order]:
    """获取订单列表"""
    dao = OrderDAO(db)
    return dao.list_all(status_filter, limit, offset)


def complete_order(db: Session, order_id: int, remarks: str | None = None) -> Order:
    """完成订单"""
    dao = OrderDAO(db)
    order = dao.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    if order.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单已完成"
        )

    return dao.update_status(order, "completed", remarks)


def get_order_stats(db: Session) -> dict:
    """获取订单统计信息"""
    dao = OrderDAO(db)

    pending_count = dao.count_by_status("pending")
    completed_count = dao.count_by_status("completed")
    total_count = pending_count + completed_count

    return {
        "total_orders": total_count,
        "pending_orders": pending_count,
        "completed_orders": completed_count
    }