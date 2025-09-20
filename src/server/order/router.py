# -*- coding: utf-8 -*-
"""
订单路由

公开接口：
- POST /api/orders/create
- GET /api/orders
- GET /api/orders/{order_id}
- PUT /api/orders/{order_id}/complete
- GET /api/orders/stats
- GET /api/orders/me
"""

from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.auth.router import (
    get_current_user,
    get_current_staff,
    get_current_admin,
)
from src.server.auth.models import User
from .schemas import OrderOut, OrderUpdate, OrderCreate
from . import service
from src.server.dao.dao_base import run_in_thread
from src.server.order.schemas import OrderStatus

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/create", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    verify_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """验证卡密并创建订单（需要登录）"""

    def _verify():
        return service.verify_activation_code(
            db, verify_data.code, current_user.id, verify_data.remarks
        )

    return await run_in_thread(_verify)


@router.get("", response_model=list[OrderOut])
async def list_orders(
    status_filter: OrderStatus | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """获取订单列表（管理员权限）"""

    def _list():
        return service.list_orders(db, status_filter, limit, offset)

    return await run_in_thread(_list)


@router.get("/pending", response_model=list[OrderOut])
async def list_pending_orders(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    """获取待使用订单列表（管理员权限）"""

    def _pending():
        return service.list_pending_orders(db)

    return await run_in_thread(_pending)


@router.get("/processing", response_model=list[OrderOut])
async def list_processing_orders(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_staff)
):
    """获取处理中订单列表（工作人员权限）"""

    def _processing():
        return service.list_processing_orders(db)

    return await run_in_thread(_processing)


@router.put("/{order_id}/complete", response_model=OrderOut)
async def complete_order(
    order_id: int,
    order_data: OrderUpdate | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """完成订单（工作人员权限）"""

    def _complete():
        remarks = order_data.remarks if order_data else None
        return service.complete_order(db, order_id, remarks)

    return await run_in_thread(_complete)


@router.get("/me", response_model=List[OrderOut])
async def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前登录用户的订单列表"""

    def _get_orders():
        return service.get_orders_by_user_id(db, current_user.id)

    return await run_in_thread(_get_orders)


@router.get("/stats")
async def get_order_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    """获取订单统计信息（管理员权限）"""

    def _stats():
        return service.get_order_stats(db)

    stats = await run_in_thread(_stats)
    return stats


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff),
):
    """获取单个订单（工作人员权限）"""

    def _get():
        return service.get_order(db, order_id)

    return await run_in_thread(_get)
