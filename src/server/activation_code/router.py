# -*- coding: utf-8 -*-
"""
卡密路由

公开接口：
- POST /api/activation-codes/generate
- GET /api/activation-codes/{card_id}
- GET /api/activation-codes/{card_id}/count
- DELETE /api/activation-codes/{card_id}
- POST /api/activation-codes/consuming
- POST /api/activation-codes/consumed
- GET /api/activation-codes/check
- GET /api/activation-codes/check-for-user
- GET /api/activation-codes/available
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.auth.router import get_current_admin, get_current_user
from src.server.auth.models import User
from .schemas import (
    ActivationCodeCreate,
    ActivationCodeOut,
    ActivationCodeVerify,
    ActivationCodeCheckResult,
    AvailableActivationCodesResponse,
    ActivationCodeExport,
)
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/activation-codes", tags=["卡密管理"])


@router.post(
    "/generate",
    response_model=list[ActivationCodeOut],
    status_code=status.HTTP_201_CREATED,
    summary="批量生成卡密",
)
async def generate_activation_codes(
    code_data: ActivationCodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """批量生成卡密（管理员权限）"""

    def _generate():
        return service.create_activation_codes(
            db=db,
            card_id=code_data.card_id,
            count=code_data.count,
            proxy_user_id=code_data.proxy_user_id,
        )

    return await run_in_thread(_generate)


@router.get(
    "/available",
    response_model=AvailableActivationCodesResponse,
    summary="获取可用卡密列表",
    responses={
        403: {"description": "无权限访问此接口"},
    },
)
async def get_available_activation_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取可用卡密列表（管理员和代理商权限）

    - 管理员：可以查看所有可用卡密，或指定代理商ID筛选
    - 代理商：只能查看自己名下的可用卡密
    - STAFF/USER：无权限访问此接口
    """

    def _get_available():
        return service.get_available_activation_codes(db=db, user=current_user)

    codes, total_count = await run_in_thread(_get_available)

    return {"codes": codes, "total_count": total_count}


@router.get(
    "/check", response_model=ActivationCodeCheckResult, summary="检查卡密可用性"
)
async def check_code_availability(
    code: str,
    db: Session = Depends(get_db),
):
    """检查卡密是否可用"""

    def _check():
        return service.is_code_available(db, code)

    return await run_in_thread(_check)


@router.get(
    "/{card_id}",
    response_model=list[ActivationCodeOut],
    summary="获取指定充值卡的卡密列表",
)
async def list_activation_codes(
    card_id: int,
    include_used: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """获取指定充值卡的所有卡密（管理员权限）"""

    def _list():
        return service.list_activation_codes_by_card(
            db=db, card_id=card_id, include_used=include_used
        )

    return await run_in_thread(_list)


@router.get("/{card_id}/count", summary="获取指定充值卡的卡密数量")
async def count_activation_codes(
    card_id: int,
    only_unused: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """获取指定充值卡的卡密数量（管理员权限）"""

    def _count():
        return service.count_activation_codes_by_card(
            db=db, card_id=card_id, only_unused=only_unused
        )

    count = await run_in_thread(_count)
    return {"card_id": card_id, "count": count, "only_unused": only_unused}


@router.post(
    "/consuming", response_model=ActivationCodeOut, summary="将卡密状态设置为使用中"
)
async def set_code_consuming(
    code_data: ActivationCodeVerify,
    db: Session = Depends(get_db),
):
    """将卡密状态设置为 consuming"""

    def _consume():
        return service.set_code_consuming(db, code_data.code)

    return await run_in_thread(_consume)


@router.post(
    "/consumed", response_model=ActivationCodeOut, summary="将卡密状态设置为已使用"
)
async def set_code_consumed(
    code_data: ActivationCodeVerify,
    db: Session = Depends(get_db),
):
    """将卡密状态设置为 consumed"""

    def _consume():
        return service.set_code_consumed(db, code_data.code)

    return await run_in_thread(_consume)


@router.delete("/{card_id}", summary="删除指定充值卡的所有卡密")
async def delete_activation_codes(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """删除指定充值卡的所有卡密（管理员权限）"""

    def _delete():
        return service.delete_activation_codes_by_card(db, card_id)

    deleted_count = await run_in_thread(_delete)
    return {"message": f"已删除 {deleted_count} 个卡密"}


@router.post(
    "/export",
    summary="批量导出卡密",
    responses={
        403: {"description": "无权限访问此接口"},
        400: {"description": "请求参数错误"},
    },
)
async def export_activation_codes(
    export_data: ActivationCodeExport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量导出卡密（管理员和代理商权限）

    - 管理员：可以导出所有卡密
    - 代理商：只能导出自己名下的卡密
    - STAFF/USER：无权限访问此接口
    """

    def _export():
        return service.mark_codes_as_exported(
            db=db, code_ids=export_data.code_ids, user=current_user
        )

    exported_count = await run_in_thread(_export)
    return {"message": f"成功导出了 {exported_count} 个卡密", "count": exported_count}
