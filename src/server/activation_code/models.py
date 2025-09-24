# -*- coding: utf-8 -*-
"""
卡密业务模型

公开接口：
- `ActivationCode`
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.server.database import Base
from src.server.card.models import Card


class CardCodeStatus(str, Enum):
    AVAILABLE = "available"
    CONSUMING = "consuming"
    CONSUMED = "consumed"


class ActivationCode(Base):
    __tablename__ = "activation_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cards.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)  # 改为 Text
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=CardCodeStatus.AVAILABLE, nullable=False
    )  # 新增 status
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 代理商关联 - 使用外键约束
    proxy_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    # 导出状态 - 用于标记卡密是否已被代理商导出
    exported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 添加与 Card 模型的关联关系
    card: Mapped["Card"] = relationship("Card", back_populates="activation_codes")
