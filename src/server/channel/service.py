# -*- coding: utf-8 -*-
"""
渠道模块服务层

公开接口：
- create_channel(db, channel_in)
- get_channel(db, channel_id)
- get_channel_by_name(db, name)
- get_channels(db, skip, limit)
- update_channel(db, channel, channel_in)
- delete_channel(db, channel_id)
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .dao import ChannelDAO
from .schemas import ChannelCreate, ChannelUpdate
from .models import Channel


def create_channel(db: Session, channel_in: ChannelCreate) -> Channel:
    """创建新渠道"""
    dao = ChannelDAO(db)
    existing_channel = dao.get_by_name(channel_in.name)
    if existing_channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="渠道名称已存在"
        )
    return dao.create(channel_in)


def get_channel(db: Session, channel_id: int) -> Channel:
    """根据ID获取渠道"""
    dao = ChannelDAO(db)
    channel = dao.get(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="渠道不存在"
        )
    return channel


def get_channel_by_name(db: Session, name: str) -> Channel:
    """根据名称获取渠道"""
    dao = ChannelDAO(db)
    channel = dao.get_by_name(name)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="渠道不存在"
        )
    return channel


def get_channels(db: Session, skip: int = 0, limit: int = 100) -> list[Channel]:
    """获取渠道列表"""
    dao = ChannelDAO(db)
    return dao.get_multi(skip, limit)


def update_channel(db: Session, channel: Channel, channel_in: ChannelUpdate) -> Channel:
    """更新渠道"""
    dao = ChannelDAO(db)
    # 检查名称是否重复（如果提供了新名称）
    if channel_in.name is not None and channel_in.name != channel.name:
        existing_channel = dao.get_by_name(channel_in.name)
        if existing_channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="渠道名称已存在"
            )
    return dao.update(channel, channel_in)


def delete_channel(db: Session, channel_id: int) -> Channel:
    """删除渠道"""
    dao = ChannelDAO(db)
    return dao.remove(channel_id)