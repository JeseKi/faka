# -*- coding: utf-8 -*-
"""
卡密路由

公开接口：
- POST /api/activation-codes/generate
- GET /api/activation-codes/{card_name}
- GET /api/activation-codes/{card_name}/count
- DELETE /api/activation-codes/{card_name}
- POST /api/activation-codes/{code}/consuming
- POST /api/activation-codes/{code}/consumed
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.auth.router import get_current_admin, get_current_user
from src.server.auth.models import User
from .schemas import ActivationCodeCreate, ActivationCodeOut
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/activation-codes", tags=["activation-codes"])


@router.post(
    "/generate",
    response_model=list[ActivationCodeOut],
    status_code=status.HTTP_201_CREATED,
)
async def generate_activation_codes(
    code_data: ActivationCodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """批量生成卡密（管理员权限）"""

    def _generate():
        return service.create_activation_codes(
            db=db, card_name=code_data.card_name, count=code_data.count
        )

    return await run_in_thread(_generate)


@router.get("/{card_name}", response_model=list[ActivationCodeOut])
async def list_activation_codes(
    card_name: str,
    include_used: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """获取指定充值卡的所有卡密（管理员权限）"""

    def _list():
        return service.list_activation_codes_by_card(
            db=db, card_name=card_name, include_used=include_used
        )

    return await run_in_thread(_list)


@router.get("/{card_name}/count")
async def count_activation_codes(
    card_name: str,
    only_unused: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """获取指定充值卡的卡密数量（管理员权限）"""

    def _count():
        return service.count_activation_codes_by_card(
            db=db, card_name=card_name, only_unused=only_unused
        )

    count = await run_in_thread(_count)
    return {"card_name": card_name, "count": count, "only_unused": only_unused}


@router.delete("/{card_name}")
async def delete_activation_codes(
    card_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """删除指定充值卡的所有卡密（管理员权限）"""

    def _delete():
        return service.delete_activation_codes_by_card(db, card_name)

    deleted_count = await run_in_thread(_delete)
    return {"message": f"已删除 {deleted_count} 个卡密"}


@router.post("/consuming", response_model=ActivationCodeOut)
async def set_code_consuming(
    code: str,
    db: Session = Depends(get_db),
):
    """将卡密状态设置为 consuming"""

    def _consume():
        return service.set_code_consuming(db, code)

    return await run_in_thread(_consume)


@router.post("/consumed", response_model=ActivationCodeOut)
async def set_code_consumed(
    code: str,
    db: Session = Depends(get_db),
):
    """将卡密状态设置为 consumed"""

    def _consume():
        return service.set_code_consumed(db, code)

    return await run_in_thread(_consume)
