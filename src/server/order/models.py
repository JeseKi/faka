# -*- coding: utf-8 -*-
"""
订单业务模型

公开接口：
- `Order`
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base
from src.server.order.schemas import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activation_code: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=OrderStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # 渠道关联 - 存储渠道ID而非外键
    channel_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # 充值卡名称
    card_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
