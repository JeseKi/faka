# -*- coding: utf-8 -*-
"""
订单完成服务模块

公开接口：
- complete_order(db, order_id, remarks)

内部方法：
- 无

说明：
- 负责订单的完成逻辑，包括状态更新、卡密状态变更等。
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..dao import OrderDAO
from ..schemas import OrderStatus, OrderOut
from src.server.activation_code.service import (
    set_code_consumed,
    get_activation_code_by_code,
)

if TYPE_CHECKING:
    pass


def complete_order(db: Session, order_id: int, remarks: str | None = None) -> OrderOut:
    """完成订单"""
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

    # 更新订单状态
    updated_order = dao.update_status(order, OrderStatus.COMPLETED, remarks)

    # 获取价格信息
    pricing = 0.0
    if updated_order.activation_code_obj and updated_order.activation_code_obj.card:
        pricing = updated_order.activation_code_obj.card.price

    # 构造 OrderOut 模型
    return OrderOut(
        id=updated_order.id,
        activation_code=updated_order.activation_code,
        status=OrderStatus(updated_order.status),
        created_at=updated_order.created_at,
        completed_at=updated_order.completed_at,
        remarks=updated_order.remarks,
        channel_id=updated_order.channel_id,
        card_name=updated_order.card_name,
        pricing=pricing,
    )
