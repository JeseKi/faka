# -*- coding: utf-8 -*-
"""
管理员路由

公开接口：
- POST /admin/users - 管理员创建用户
- PUT /admin/users/{user_id} - 管理员更新指定用户
- GET /admin/users - 管理员获取用户列表
- GET /admin/users/{user_id} - 管理员获取指定用户
- DELETE /admin/users/{user_id} - 管理员删除指定用户
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from src.server.database import get_db
from src.server.dao.dao_base import run_in_thread
from ..models import User
from .. import service
from ..schemas import (
    Role,
    UserProfile,
    AdminUserCreate,
    AdminUserUpdate,
    UserListResponse,
)
from src.server.utils import get_current_admin

router = APIRouter(prefix="/api/auth", tags=["管理员"])


@router.post(
    "/admin/users",
    response_model=UserProfile,
    status_code=status.HTTP_201_CREATED,
    summary="管理员创建用户",
)
async def admin_create_user(
    user_data: AdminUserCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """管理员创建用户接口"""
    # 检查用户名是否已被注册
    db_user = service.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被注册"
        )

    # 检查邮箱是否已被注册
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
        )

    # 如果是创建 STAFF 用户，需要检查渠道是否存在
    if user_data.role == Role.STAFF and user_data.channel_id is not None:
        from src.server.channel.models import Channel

        channel = db.query(Channel).filter(Channel.id == user_data.channel_id).first()
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="指定的渠道不存在"
            )

    new_user = service.admin_create_user(db=db, user_data=user_data)
    return new_user


@router.put(
    "/admin/users/{user_id}",
    response_model=UserProfile,
    summary="管理员更新指定用户",
    responses={
        404: {"description": "用户不存在"},
        400: {"description": "邮箱已被使用或渠道不存在"},
        403: {"description": "无权限"},
    },
)
async def admin_update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """管理员更新指定ID的用户信息接口"""
    try:
        updated_user = service.admin_update_user(
            db=db, user_id=user_id, user_data=user_data
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/admin/users",
    response_model=UserListResponse,
    summary="管理员获取用户列表",
    responses={
        403: {"description": "无权限"},
    },
)
async def admin_get_users(
    role: Optional[Role] = None,
    page: int = 1,
    page_size: int = 50,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """管理员获取用户列表接口（支持按角色筛选）"""

    def _get_users():
        return service.get_users_by_role(
            db=db, role=role, page=page, page_size=page_size
        )

    users, total_count = await run_in_thread(_get_users)
    return {"users": users, "total_count": total_count}


@router.get(
    "/admin/users/{user_id}",
    response_model=UserProfile,
    summary="管理员获取指定用户",
    responses={
        404: {"description": "用户不存在"},
        403: {"description": "无权限"},
    },
)
async def admin_get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """管理员获取指定ID的用户信息接口"""
    user = service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


@router.delete(
    "/admin/users/{user_id}",
    summary="管理员删除指定用户",
    responses={
        404: {"description": "用户不存在"},
        400: {"description": "不能删除管理员用户"},
        403: {"description": "无权限"},
    },
)
async def admin_delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """管理员删除指定ID的用户接口"""
    try:
        success = service.delete_user(db=db, user_id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )
        return {"message": "用户删除成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
