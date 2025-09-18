# -*- coding: utf-8 -*-
"""
销售记录业务模型

公开接口：
- `Sale`
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activation_code: Mapped[str] = mapped_column(String(36), nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False)
    sale_price: Mapped[float] = mapped_column(Float, nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)