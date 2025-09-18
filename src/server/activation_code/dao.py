# -*- coding: utf-8 -*-
"""
卡密模块 DAO

公开接口：
- `ActivationCodeDAO`
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO
from .models import ActivationCode


class ActivationCodeDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create_batch(self, card_name: str, count: int) -> list[ActivationCode]:
        """批量创建卡密"""
        codes = []
        for _ in range(count):
            code = str(uuid.uuid4())
            activation_code = ActivationCode(
                card_name=card_name,
                code=code,
                is_used=False,
                created_at=datetime.now(timezone.utc),
            )
            codes.append(activation_code)
            self.db_session.add(activation_code)

        self.db_session.commit()
        for code in codes:
            self.db_session.refresh(code)
        return codes

    def get_by_code(self, code: str) -> ActivationCode | None:
        """通过卡密获取记录"""
        return (
            self.db_session.query(ActivationCode)
            .filter(ActivationCode.code == code)
            .first()
        )

    def get_available_by_card_name(self, card_name: str) -> ActivationCode | None:
        """获取指定充值卡的可用卡密（未使用）"""
        return (
            self.db_session.query(ActivationCode)
            .filter(ActivationCode.card_name == card_name, ~ActivationCode.is_used)
            .first()
        )

    def mark_as_used(self, activation_code: ActivationCode) -> ActivationCode:
        """标记卡密为已使用"""
        activation_code.is_used = True
        activation_code.used_at = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(activation_code)
        return activation_code

    def list_by_card_name(
        self, card_name: str, include_used: bool = False
    ) -> list[ActivationCode]:
        """获取指定充值卡的所有卡密"""
        query = self.db_session.query(ActivationCode).filter(
            ActivationCode.card_name == card_name
        )
        if not include_used:
            query = query.filter(~ActivationCode.is_used)
        return query.order_by(ActivationCode.created_at.desc()).all()

    def count_by_card_name(self, card_name: str, only_unused: bool = True) -> int:
        """统计指定充值卡的卡密数量"""
        query = self.db_session.query(ActivationCode).filter(
            ActivationCode.card_name == card_name
        )
        if only_unused:
            query = query.filter(~ActivationCode.is_used)
        return query.count()

    def delete_by_card_name(self, card_name: str) -> int:
        """删除指定充值卡的所有卡密，返回删除的数量"""
        deleted_count = (
            self.db_session.query(ActivationCode)
            .filter(ActivationCode.card_name == card_name)
            .delete()
        )
        self.db_session.commit()
        return deleted_count
