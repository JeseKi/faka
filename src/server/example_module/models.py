# -*- coding: utf-8 -*-
"""
示例业务模型（模板版）

公开接口：
- `Item`
"""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base


class Item(Base):
    __tablename__ = "example_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
