# -*- coding: utf-8 -*-
"""
订单模块服务层

公开接口：
- verify_activation_code(db, code, user_id)
- create_order(db, activation_code, user_id, status, remarks)
- get_order(db, order_id)
- list_pending_orders(db)
- list_orders(db, status_filter, limit, offset)
- complete_order(db, order_id, remarks)
- get_order_stats(db)
- get_orders_by_user_id(db, user_id)

内部方法：
- 无

说明：
- 服务层承载业务逻辑，路由层只做参数校验与装配。
"""

from __future__ import annotations
from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .dao import OrderDAO
from .models import Order
from .schemas import OrderStatus


def verify_activation_code(
    db: Session, code: str, user_id: int, remarks: str | None = None
) -> Order:
    """验证卡密并创建订单"""
    from src.server.activation_code.service import set_code_consuming

    activation_code = set_code_consuming(db, code)
    order = create_order(db, activation_code.code, user_id, OrderStatus.PROCESSING, remarks)

    # # 设置订单状态 # TODO: 暂时不使用，因为目前的阶段不需要验证卡密是否属于用户
    # dao = OrderDAO(db)
    # order = dao.get_by_activation_code(activation_code.code)
    # if not order:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND, detail=f"未找到卡密：{code}"
    #     )
# 
    # if order.user_id != user_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail=f"卡密不属于用户：{user_id}"
    #     )
# 
    # order = dao.update_status(
    #     order=order, status=OrderStatus.PROCESSING, remarks=remarks
    # )

    return order


def create_order(
    db: Session,
    activation_code: str,
    user_id: int,
    status: OrderStatus = OrderStatus.PROCESSING,
    remarks: str | None = None,
) -> Order:
    """创建订单"""
    dao = OrderDAO(db)
    return dao.create(activation_code, user_id, status, remarks)


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


def list_processing_orders(db: Session) -> list[Order]:
    """获取所有处理中订单"""
    dao = OrderDAO(db)
    return dao.list_processing()


def list_orders(
    db: Session,
    status_filter: OrderStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Order]:
    """获取订单列表"""
    dao = OrderDAO(db)
    return dao.list_all(status_filter, limit, offset)


def complete_order(db: Session, order_id: int, remarks: str | None = None) -> Order:
    """完成订单"""
    from src.server.activation_code.service import (
        set_code_consumed,
        get_activation_code_by_code,
    )

    dao = OrderDAO(db)
    order = dao.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    if order.status == OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="订单已完成"
        )

    # 获取对应的卡密记录
    activation_code = get_activation_code_by_code(db, order.activation_code)
    if not activation_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="关联的卡密不存在"
        )

    # 将卡密状态设置为 consumed
    set_code_consumed(db, activation_code.code)

    return dao.update_status(order, OrderStatus.COMPLETED, remarks)


def get_orders_by_user_id(db: Session, user_id: int) -> List[Order]:
    """获取指定用户的所有订单"""
    dao = OrderDAO(db)
    return dao.get_orders_by_user_id(user_id)


def get_order_stats(db: Session) -> dict:
    """获取订单统计信息"""
    dao = OrderDAO(db)

    pending_count = dao.count_by_status(OrderStatus.PENDING)
    completed_count = dao.count_by_status(OrderStatus.COMPLETED)
    total_count = pending_count + completed_count

    return {
        "total_orders": total_count,
        "pending_orders": pending_count,
        "completed_orders": completed_count,
    }
