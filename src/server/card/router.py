# -*- coding: utf-8 -*-
"""
充值卡路由

公开接口：
- POST /api/cards
- GET /api/cards
- GET /api/cards/{card_id}
- PUT /api/cards/{card_id}
- DELETE /api/cards/{card_id}
- GET /api/cards/{card_name}/stock
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.auth.router import get_current_admin, get_current_user
from src.server.auth.models import User
from src.server.auth.schemas import Role
from .schemas import CardCreate, CardUpdate, CardOut
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.post("", response_model=CardOut, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """创建充值卡（管理员权限）"""

    def _create():
        return service.create_card(
            db=db,
            card_in=card_data
        )

    return await run_in_thread(_create)


@router.get("", response_model=list[CardOut])
async def list_cards(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取充值卡列表"""
    
    def _list():
        # 如果是员工，只返回其渠道下的卡片
        if current_user.role == Role.STAFF:
            # 检查员工是否有渠道ID
            if current_user.channel_id is None:
                return []
            # 实现根据员工渠道过滤卡片的逻辑
            return service.list_cards_by_channel(db, current_user.channel_id, include_inactive)
        return service.list_cards(db, include_inactive)

    return await run_in_thread(_list)


@router.get("/{card_id}", response_model=CardOut)
async def get_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个充值卡"""
    
    def _get():
        # 如果是员工，需要检查卡片是否属于其渠道
        card = service.get_card(db, card_id)
        if current_user.role == Role.STAFF:
            # 实现渠道检查逻辑
            if card.channel_id != current_user.channel_id:
                from fastapi import HTTPException, status
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该充值卡")
        return card

    return await run_in_thread(_get)


@router.put("/{card_id}", response_model=CardOut)
async def update_card(
    card_id: int,
    card_data: CardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """更新充值卡（管理员权限）"""

    def _update():
        card = service.get_card(db, card_id)
        return service.update_card(
            db=db,
            card=card,
            card_in=card_data
        )

    return await run_in_thread(_update)


@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """删除充值卡（管理员权限）"""

    def _delete():
        card = service.get_card(db, card_id)
        service.delete_card(db, card)

    await run_in_thread(_delete)
    return {"message": "充值卡已删除"}


@router.get("/{card_name}/stock")
async def get_card_stock(
    card_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """获取充值卡库存数量（管理员权限）"""

    def _get_stock():
        return service.get_card_stock(db, card_name)

    stock_count = await run_in_thread(_get_stock)
    return {"card_name": card_name, "stock": stock_count}