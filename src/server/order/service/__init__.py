# -*- coding: utf-8 -*-
"""
订单服务模块统一导出接口

此模块统一导出订单服务的所有公开接口，确保对上层调用的兼容性。

公开接口：
- verify_activation_code(db, code, channel_id, remarks, card_name)
- create_order(db, activation_code, channel_id, status, remarks, card_name)
- get_order(db, order_id)
- list_pending_orders(db)
- list_orders(db, status_filter, limit, offset)
- complete_order(db, order_id, remarks)
- get_order_stats(db)
- get_orders_by_user_id(db, user_id)
"""

from __future__ import annotations

# 从各子模块导入所有公开接口
from .creation import verify_activation_code, create_order
from .retrieval import (
    get_order,
    list_pending_orders,
    list_processing_orders,
    list_orders,
    get_orders_by_user_id,
)
from .completion import complete_order
from .stats import get_order_stats

# 统一导出所有公开接口
__all__ = [
    "verify_activation_code",
    "create_order",
    "get_order",
    "list_pending_orders",
    "list_processing_orders",
    "list_orders",
    "complete_order",
    "get_order_stats",
    "get_orders_by_user_id",
]
