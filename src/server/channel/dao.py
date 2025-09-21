# -*- coding: utf-8 -*-
"""
渠道模块数据访问对象（DAO）

公开接口：
- `ChannelDAO`
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from .models import Channel
from .schemas import ChannelCreate, ChannelUpdate
from src.server.dao.dao_base import BaseDAO


class ChannelDAO(BaseDAO):
    """
    渠道数据访问对象，继承自 BaseDAO。
    提供对 Channel 模型的 CRUD 操作。
    """

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def get(self, id: int) -> Channel | None:
        """根据ID获取渠道"""
        return self.db_session.query(Channel).filter(Channel.id == id).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Channel]:
        """获取多个渠道"""
        return self.db_session.query(Channel).offset(skip).limit(limit).all()

    def get_by_name(self, name: str) -> Channel | None:
        """根据名称获取渠道"""
        return self.db_session.query(Channel).filter(Channel.name == name).first()

    def create(self, obj_in: ChannelCreate) -> Channel:
        """创建新渠道"""
        try:
            db_obj = Channel(name=obj_in.name, description=obj_in.description)
            self.db_session.add(db_obj)
            self.db_session.commit()
            self.db_session.refresh(db_obj)
            return db_obj
        except IntegrityError:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="渠道名称已存在"
            )

    def update(self, db_obj: Channel, obj_in: ChannelUpdate) -> Channel:
        """更新渠道"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db_session.add(db_obj)
        self.db_session.commit()
        self.db_session.refresh(db_obj)
        return db_obj

    def remove(self, id: int) -> Channel:
        """删除渠道"""
        obj = self.get(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="渠道不存在"
            )
        self.db_session.delete(obj)
        self.db_session.commit()
        return obj
