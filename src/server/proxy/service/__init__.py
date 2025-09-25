# -*- coding: utf-8 -*-
"""
代理商服务模块

此模块将代理商相关的服务功能组织到不同的子模块中：
- association: 代理商与充值卡关联管理
- revenue: 代理商销售额统计

公开接口：
- `link_proxy_to_cards`、`unlink_proxy_from_cards`
- `get_proxy_cards`、`get_proxy_card_associations`
- `check_proxy_card_access`、`get_available_cards_for_proxy`
- `get_all_proxy_associations`
- `calculate_proxy_revenue`

内部方法：
- `_calculate_single_proxy_revenue`
"""

from .association import (
    link_proxy_to_cards,
    unlink_proxy_from_cards,
    get_proxy_cards,
    get_proxy_card_associations,
    check_proxy_card_access,
    get_available_cards_for_proxy,
    get_all_proxy_associations,
)

from .revenue import (
    calculate_proxy_revenue,
    _calculate_single_proxy_revenue,
)

__all__ = [
    # 关联管理
    "link_proxy_to_cards",
    "unlink_proxy_from_cards",
    "get_proxy_cards",
    "get_proxy_card_associations",
    "check_proxy_card_access",
    "get_available_cards_for_proxy",
    "get_all_proxy_associations",
    # 销售额统计
    "calculate_proxy_revenue",
    # 内部方法
    "_calculate_single_proxy_revenue",
]
