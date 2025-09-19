# -*- coding: utf-8 -*-
"""
卡密业务模型

公开接口：
- `ActivationCode`
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base


class CardCodeStatus(str, Enum):
    AVAILABLE = "available"
    CONSUMING = "consuming"
    CONSUMED = "consumed"


class ActivationCode(Base):
    __tablename__ = "activation_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)  # 改为 Text
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=CardCodeStatus.AVAILABLE, nullable=False)  # 新增 status
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    