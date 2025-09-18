# -*- coding: utf-8 -*-
"""
充值卡业务模型

公开接口：
- `Card`
"""

from __future__ import annotations

from sqlalchemy import Integer, String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
