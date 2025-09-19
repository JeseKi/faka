# -*- coding: utf-8 -*-
"""
销售路由

公开接口：
- POST /api/sales/purchase
- GET /api/sales
- GET /api/sales/stats
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.auth.router import get_current_user
from src.server.auth.models import User
from .schemas import SaleCreate, SaleOut
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/sales", tags=["sales"])


@router.post("/purchase", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
async def purchase_card(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """购买充值卡（前台用户，无需登录）"""

    def _purchase():
        sale = service.purchase_card(
            db=db,
            card_name=sale_data.card_name,
            user_email=sale_data.user_email,
            user_id=current_user.id,
        )

        # 发送邮件（这里先返回销售记录，邮件发送逻辑在后续实现）
        # TODO: 实现邮件发送功能

        return sale

    return await run_in_thread(_purchase)


@router.get("", response_model=list[SaleOut])
async def list_sales(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取销售记录列表（管理员权限）"""

    def _list():
        return service.list_sales(db, limit, offset)

    return await run_in_thread(_list)


@router.get("/stats")
async def get_sales_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """获取销售统计信息（管理员权限）"""

    def _stats():
        return service.get_sales_stats(db)

    stats = await run_in_thread(_stats)
    return stats


@router.get("/user/{user_email}", response_model=list[SaleOut])
async def get_user_sales(
    user_email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定用户的购买记录（管理员权限）"""

    def _user_sales():
        return service.get_user_sales(db, user_email)

    return await run_in_thread(_user_sales)
