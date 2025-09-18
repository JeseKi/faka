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
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.config import global_config
from .config import auth_config
from .models import User
from . import service
from .schemas import (
    PasswordChange,
    TokenResponse,
    UserCreate,
    UserProfile,
    UserUpdate,
    UserLogin,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if global_config.app_env in ["dev", "test"] and token == auth_config.test_token:
        user = db.query(User).filter(User.id == 1).first()
        if user:
            return user
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, auth_config.jwt_secret_key, algorithms=[auth_config.jwt_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = service.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/login", response_model=TokenResponse)
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


@router.post(
    "/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = service.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被注册"
        )
    new_user = service.create_user(db=db, user_data=user_data)
    return new_user


@router.post("/refresh", response_model=TokenResponse)
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


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserProfile)
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


@router.put("/password")
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
