# -*- coding: utf-8 -*-
"""
订单路由

公开接口：
- POST /api/orders/verify
- GET /api/orders
- GET /api/orders/{order_id}
- PUT /api/orders/{order_id}/complete
- GET /api/orders/stats
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.auth.router import get_current_user
from src.server.auth.models import User
from .schemas import OrderOut, OrderUpdate, OrderVerify
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/verify", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def verify_activation_code(
    verify_data: OrderVerify, db: Session = Depends(get_db)
):
    """验证卡密并创建订单（外部服务调用，无需登录）"""

    def _verify():
        return service.verify_activation_code(db, verify_data.code)

    return await run_in_thread(_verify)


@router.get("", response_model=list[OrderOut])
async def list_orders(
    status_filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取订单列表（工作人员权限）"""

    def _list():
        return service.list_orders(db, status_filter, limit, offset)

    return await run_in_thread(_list)


@router.get("/pending", response_model=list[OrderOut])
async def list_pending_orders(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """获取待处理订单列表（工作人员权限）"""

    def _pending():
        return service.list_pending_orders(db)

    return await run_in_thread(_pending)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个订单（工作人员权限）"""

    def _get():
        return service.get_order(db, order_id)

    return await run_in_thread(_get)


@router.put("/{order_id}/complete", response_model=OrderOut)
async def complete_order(
    order_id: int,
    order_data: OrderUpdate | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """完成订单（工作人员权限）"""

    def _complete():
        remarks = order_data.remarks if order_data else None
        return service.complete_order(db, order_id, remarks)

    return await run_in_thread(_complete)


@router.get("/stats")
async def get_order_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """获取订单统计信息（工作人员权限）"""

    def _stats():
        return service.get_order_stats(db)

    stats = await run_in_thread(_stats)
    return stats
