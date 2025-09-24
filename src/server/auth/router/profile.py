# -*- coding: utf-8 -*-
"""
用户资料路由

公开接口：
- GET /profile - 获取用户个人资料
- PUT /profile - 更新用户个人资料
- PUT /password - 修改用户密码
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from ..models import User
from .. import service
from ..schemas import (
    PasswordChange,
    UserProfile,
    UserUpdate,
)
from src.server.utils import get_current_user

router = APIRouter(prefix="/api/auth", tags=["用户资料"])


@router.get("/profile", response_model=UserProfile, summary="获取用户个人资料")
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取用户个人资料接口"""
    return current_user


@router.put("/profile", response_model=UserProfile, summary="更新用户个人资料")
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新用户个人资料接口"""
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
    """修改用户密码接口"""
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
