# -*- coding: utf-8 -*-
"""
卡密业务模型

公开接口：
- `ActivationCode`
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base


class ActivationCode(Base):
    __tablename__ = "activation_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
