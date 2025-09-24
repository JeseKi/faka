# -*- coding: utf-8 -*-
"""
认证模块 DAO（模板版）

公开接口：
- `UserDAO`

内部方法：
- get_by_role / count_by_role / get_all / count_all

说明：
- 提供用户读取/写入的持久化封装，业务逻辑放在 service。
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO
from .models import User
from .schemas import Role


class UserDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def get_by_username(self, username: str) -> User | None:
        return self.db_session.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> User | None:
        """根据用户ID获取用户信息"""
        return self.db_session.query(User).filter(User.id == user_id).first()

    def create(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: Role,
        channel_id: int | None = None,
    ) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            channel_id=channel_id,
        )
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def update(self, user: User, **fields) -> User:
        for k, v in fields.items():
            setattr(user, k, v)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def get_staff_by_channel_id(self, channel_id: int) -> list[User]:
        """获取指定渠道的所有员工用户"""
        return (
            self.db_session.query(User)
            .filter(User.role == Role.STAFF, User.channel_id == channel_id)
            .all()
        )

    def get_by_role(self, role: Role, page: int = 1, page_size: int = 50) -> list[User]:
        """根据角色获取用户列表，支持分页"""
        offset = (page - 1) * page_size
        return (
            self.db_session.query(User)
            .filter(User.role == role)
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def count_by_role(self, role: Role) -> int:
        """根据角色统计用户数量"""
        return self.db_session.query(User).filter(User.role == role).count()

    def get_all(self, page: int = 1, page_size: int = 50) -> list[User]:
        """获取所有用户列表，支持分页"""
        offset = (page - 1) * page_size
        return self.db_session.query(User).offset(offset).limit(page_size).all()

    def count_all(self) -> int:
        """统计所有用户数量"""
        return self.db_session.query(User).count()
