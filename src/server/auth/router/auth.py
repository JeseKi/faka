# -*- coding: utf-8 -*-
"""
核心认证路由

公开接口：
- POST /login - 用户登录
- POST /refresh - 刷新访问令牌
- POST /send-verification-code - 发送邮箱验证码
- POST /register-with-code - 使用验证码注册用户
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from src.server.database import get_db
from ..models import User
from .. import service
from ..schemas import (
    TokenResponse,
    UserLogin,
    VerificationCodeRequest,
    UserRegisterWithCode,
    UserProfile,
    UserCreate,
)
from src.server.utils import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login_for_access_token(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录接口"""
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
    """发送邮箱验证码接口"""
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
    """使用验证码注册用户接口"""
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
    """刷新访问令牌接口"""
    new_access_token = service.create_access_token(data={"sub": current_user.username})
    new_refresh_token = service.create_refresh_token(
        data={"sub": current_user.username}
    )
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
