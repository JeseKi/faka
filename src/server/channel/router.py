# -*- coding: utf-8 -*-
"""
渠道模块 API 路由

公开接口：
- `/api/channels` - 渠道管理相关端点
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.server.database import get_db
from src.server.auth.router import get_current_admin
from src.server.auth.models import User
from . import schemas, service

router = APIRouter(prefix="/api/channels", tags=["Channel Management"])


@router.post("/", response_model=schemas.ChannelOut, summary="创建渠道")
def create_channel(
    channel_in: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    创建一个新的渠道。

    **权限要求**: 仅限管理员 (admin) 操作。
    """
    return service.create_channel(db, channel_in)


@router.get("/{channel_id}", response_model=schemas.ChannelOut, summary="获取渠道详情")
def read_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    根据ID获取渠道详情。

    **权限要求**: 管理员 (admin)。
    """
    return service.get_channel(db, channel_id)


@router.get("/", response_model=List[schemas.ChannelOut], summary="获取渠道列表")
def read_channels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    获取渠道列表。

    **权限要求**: 管理员 (admin)。
    """
    return service.get_channels(db, skip, limit)


@router.put("/{channel_id}", response_model=schemas.ChannelOut, summary="更新渠道")
def update_channel(
    channel_id: int,
    channel_in: schemas.ChannelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    更新指定ID的渠道信息。

    **权限要求**: 仅限管理员 (admin) 操作。
    """
    channel = service.get_channel(db, channel_id)
    return service.update_channel(db, channel, channel_in)


@router.delete("/{channel_id}", response_model=schemas.ChannelOut, summary="删除渠道")
def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    删除指定ID的渠道。

    **权限要求**: 仅限管理员 (admin) 操作。
    """
    return service.delete_channel(db, channel_id)
