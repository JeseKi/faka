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
from src.server.auth.router import get_current_user
from src.server.auth.models import User
from .schemas import CardCreate, CardUpdate, CardOut
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.post("", response_model=CardOut, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建充值卡（管理员权限）"""

    def _create():
        return service.create_card(
            db=db,
            name=card_data.name,
            description=card_data.description,
            price=card_data.price,
            is_active=card_data.is_active,
        )

    return await run_in_thread(_create)


@router.get("", response_model=list[CardOut])
async def list_cards(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取充值卡列表（管理员权限）"""

    def _list():
        return service.list_cards(db, include_inactive)

    return await run_in_thread(_list)


@router.get("/{card_id}", response_model=CardOut)
async def get_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个充值卡（管理员权限）"""

    def _get():
        return service.get_card(db, card_id)

    return await run_in_thread(_get)


@router.put("/{card_id}", response_model=CardOut)
async def update_card(
    card_id: int,
    card_data: CardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新充值卡（管理员权限）"""

    def _update():
        card = service.get_card(db, card_id)
        return service.update_card(
            db=db,
            card=card,
            name=card_data.name,
            description=card_data.description,
            price=card_data.price,
            is_active=card_data.is_active,
        )

    return await run_in_thread(_update)


@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    """获取充值卡库存数量（管理员权限）"""

    def _get_stock():
        return service.get_card_stock(db, card_name)

    stock_count = await run_in_thread(_get_stock)
    return {"card_name": card_name, "stock": stock_count}


@router.post("/{card_name}/generate-codes", status_code=status.HTTP_201_CREATED)
async def generate_activation_codes_for_card(
    card_name: str,
    count: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """为指定充值卡批量生成卡密（管理员权限）"""

    def _generate():
        # 验证充值卡是否存在
        _ = service.get_card_by_name(db, card_name)
        # 生成卡密
        from src.server.activation_code import service as activation_service

        return activation_service.create_activation_codes(db, card_name, count)

    codes = await run_in_thread(_generate)
    return {
        "message": f"为充值卡 '{card_name}' 生成了 {len(codes)} 个卡密",
        "card_name": card_name,
        "generated_count": len(codes),
    }
