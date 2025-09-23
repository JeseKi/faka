# -*- coding: utf-8 -*-
"""
充值卡业务模型

公开接口：
- `Card`
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.server.database import Base

if TYPE_CHECKING:
    from src.server.activation_code.models import ActivationCode


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 渠道关联 - 存储渠道ID而非外键
    channel_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # 添加与 ActivationCode 模型的反向关联关系
    activation_codes: Mapped[list["ActivationCode"]] = relationship(
        "ActivationCode", back_populates="card"
    )  # type: ignore
