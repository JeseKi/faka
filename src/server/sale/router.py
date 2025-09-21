# -*- coding: utf-8 -*-
"""
销售路由

公开接口：
- POST /api/sales/purchase
- GET /api/sales
- GET /api/sales/stats
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status, HTTPException
from loguru import logger
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.auth.router import get_current_user, get_current_admin
from src.server.auth.models import User
from src.server.mail_sender import (
    MailAddress,
    PurchaseMailPayload,
    send_purchase_confirmation_email,
)
from .schemas import SaleCreate, SaleOut
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/sales", tags=["销售管理"])


@router.post("/purchase", response_model=SaleOut, status_code=status.HTTP_201_CREATED, summary="购买充值卡")
async def purchase_card(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """购买充值卡"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="购买充值卡失败"
    )  # TODO: 目前阶段暂时关闭购买功能

    def _purchase():
        sale = service.purchase_card(
            db=db,
            card_name=sale_data.card_name,
            user_email=sale_data.user_email,
            user_id=current_user.id,
        )

        recipient = MailAddress(
            email=sale.user_email,
            name=current_user.name or current_user.username,
        )
        mail_result = send_purchase_confirmation_email(
            PurchaseMailPayload(
                recipient=recipient,
                card_name=sale.card_name,
                activation_code=sale.activation_code,
                sale_price=sale.sale_price,
                purchased_at=sale.purchased_at,
            )
        )

        if not mail_result.success:
            logger.error(
                f"购买成功邮件发送失败，销售编号 {sale.id}，错误：{mail_result.error}"
            )

        return sale

    return await run_in_thread(_purchase)


@router.get("", response_model=list[SaleOut], summary="获取销售记录列表")
async def list_sales(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """获取销售记录列表（管理员权限）"""

    def _list():
        return service.list_sales(db, limit, offset)

    return await run_in_thread(_list)


@router.get("/stats", summary="获取销售统计信息")
async def get_sales_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    """获取销售统计信息（管理员权限）"""

    def _stats():
        # TODO: 实现销售统计功能
        return {"message": "销售统计功能尚未实现"}

    stats = await run_in_thread(_stats)
    return stats


@router.get("/user/{user_email}", response_model=list[SaleOut], summary="获取指定用户的销售记录")
async def get_user_sales(
    user_email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """获取指定用户的购买记录（管理员权限）"""

    def _user_sales():
        # TODO: 实现获取用户销售记录功能
        return []

    return await run_in_thread(_user_sales)
