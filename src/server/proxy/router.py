# -*- coding: utf-8 -*-
"""
代理商管理路由

公开接口：
- POST /api/proxy/link
- POST /api/proxy/unlink
- GET /api/proxy/{proxy_user_id}/cards
- GET /api/proxy/associations
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.server.database import get_db
from src.server.auth.router import get_current_admin
from src.server.auth.models import User
from .schemas import (
    ProxyCardLinkRequest,
    ProxyCardUnlinkRequest,
    ProxyCardListResponse,
    ProxyCardAssociationOut,
)
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/proxy", tags=["代理商管理"])


async def get_current_proxy(
    current_user: User = Depends(get_current_admin),
) -> User:
    """获取当前代理商用户"""
    if current_user.role != "proxy":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    return current_user


@router.post(
    "/link",
    response_model=List[ProxyCardAssociationOut],
    status_code=status.HTTP_201_CREATED,
    summary="为代理商绑定充值卡",
    responses={
        400: {"description": "代理商不存在、角色错误或充值卡不存在"},
        403: {"description": "无权限"},
    },
)
async def link_proxy_to_cards(
    link_request: ProxyCardLinkRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """为代理商绑定多个充值卡（管理员权限）"""

    def _link():
        return service.link_proxy_to_cards(
            db=db,
            proxy_user_id=link_request.proxy_user_id,
            card_ids=link_request.card_ids,
        )

    try:
        return await run_in_thread(_link)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/unlink",
    summary="为代理商解绑充值卡",
    responses={
        400: {"description": "代理商不存在或角色错误"},
        403: {"description": "无权限"},
    },
)
async def unlink_proxy_from_cards(
    unlink_request: ProxyCardUnlinkRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """为代理商解绑多个充值卡（管理员权限）"""

    def _unlink():
        return service.unlink_proxy_from_cards(
            db=db,
            proxy_user_id=unlink_request.proxy_user_id,
            card_ids=unlink_request.card_ids,
        )

    try:
        deleted_count = await run_in_thread(_unlink)
        return {"message": f"成功解绑 {deleted_count} 个充值卡"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{proxy_user_id}/cards",
    response_model=ProxyCardListResponse,
    summary="获取代理商绑定的充值卡列表",
    responses={
        403: {"description": "无权限"},
        404: {"description": "代理商不存在"},
    },
)
async def get_proxy_cards(
    proxy_user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """获取指定代理商绑定的充值卡列表（管理员权限）"""

    def _get_cards():
        return service.get_proxy_cards(db=db, proxy_user_id=proxy_user_id)

    cards = await run_in_thread(_get_cards)

    return {"proxy_user_id": proxy_user_id, "cards": cards, "total_count": len(cards)}


@router.get(
    "/associations",
    response_model=List[ProxyCardAssociationOut],
    summary="获取所有代理商关联记录",
    responses={
        403: {"description": "无权限"},
    },
)
async def get_all_proxy_associations(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """获取所有代理商与充值卡的关联记录（管理员权限）"""

    def _get_associations():
        return service.get_all_proxy_associations(db=db)

    return await run_in_thread(_get_associations)
