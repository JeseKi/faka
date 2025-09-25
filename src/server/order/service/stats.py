# -*- coding: utf-8 -*-
"""
订单统计服务模块

公开接口：
- get_order_stats(db)

内部方法：
- 无

说明：
- 负责订单的统计逻辑，包括订单数量统计等。
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from ..dao import OrderDAO
from ..schemas import OrderStatus

if TYPE_CHECKING:
    pass


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
