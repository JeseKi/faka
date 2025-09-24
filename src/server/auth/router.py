# -*- coding: utf-8 -*-
"""
认证路由（模板版）

公开接口：
- POST /api/auth/login
- POST /api/auth/register
- POST /api/auth/refresh
- GET /api/auth/profile
- PUT /api/auth/profile
- PUT /api/auth/password
- POST /api/auth/send-verification-code
- POST /api/auth/register-with-code
- PUT /api/auth/admin/users/{user_id}
- GET /api/auth/admin/users
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session
from typing import Optional

from src.server.database import get_db
from .models import User
from . import service
from src.server.dao.dao_base import run_in_thread
from .schemas import (
    PasswordChange,
    Role,
    TokenResponse,
    UserCreate,
    UserProfile,
    UserUpdate,
    UserLogin,
    VerificationCodeRequest,
    UserRegisterWithCode,
    AdminUserCreate,
    AdminUserUpdate,
    UserListResponse,
)
from src.server.utils import get_current_user, get_current_admin

router = APIRouter(prefix="/api/auth", tags=["用户管理"])


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login_for_access_token(login_data: UserLogin, db: Session = Depends(get_db)):
    user = service.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="不正确的用户名或密码",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = service.create_access_token(data={"sub": user.username})
    refresh_token = service.create_refresh_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/send-verification-code", summary="发送邮箱验证码")
async def send_verification_code(
    request: VerificationCodeRequest, db: Session = Depends(get_db)
):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="验证码发送失败"
    )  # TODO: 目前阶段暂时关闭注册功能
    # 检查邮箱是否已被注册
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
        )

    # 生成并发送验证码
    try:
        service.send_verification_code(request.email)
    except RuntimeError as exc:
        logger.error(f"发送验证码邮件失败：{exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="验证码发送失败"
        )
    return {"message": "验证码已发送"}


@router.post(
    "/register-with-code",
    response_model=UserProfile,
    status_code=status.HTTP_201_CREATED,
    summary="使用验证码注册用户",
)
async def register_user_with_code(
    user_data: UserRegisterWithCode, db: Session = Depends(get_db)
):
    # 检查用户名是否已被注册
    db_user = service.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被注册"
        )

    # 验证验证码
    if not service.verify_code(user_data.email, user_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证码无效或已过期"
        )

    # 创建用户
    user_create = UserCreate(
        username=user_data.username, email=user_data.email, password=user_data.password
    )
    new_user = service.create_user(db=db, user_data=user_create)
    return new_user


@router.post("/refresh", response_model=TokenResponse, summary="刷新访问令牌")
async def refresh_access_token(current_user: User = Depends(get_current_user)):
    new_access_token = service.create_access_token(data={"sub": current_user.username})
    new_refresh_token = service.create_refresh_token(
        data={"sub": current_user.username}
    )
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/profile", response_model=UserProfile, summary="获取用户个人资料")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserProfile, summary="更新用户个人资料")
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_data.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被使用"
            )
    updated_user = service.update_user(db=db, user=current_user, user_data=user_data)
    return updated_user


@router.put("/password", summary="修改用户密码")
async def change_current_user_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = service.change_password(
        db=db,
        user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确"
        )
    return {"message": "密码修改成功"}


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
    """管理员创建用户"""
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
    """管理员更新指定ID的用户信息"""
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
    """管理员获取用户列表（支持按角色筛选）

    - 管理员：可以查看所有用户，或指定角色筛选
    - 支持分页查询
    """

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
    """管理员获取指定ID的用户信息"""
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
    """管理员删除指定ID的用户"""
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
