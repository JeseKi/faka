# -*- coding: utf-8 -*-
"""
渠道业务模型

公开接口：
- `Channel`
"""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<Channel(id={self.id}, name='{self.name}')>"