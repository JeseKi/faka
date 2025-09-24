# -*- coding: utf-8 -*-
"""
代理商管理业务模型

公开接口：
- `ProxyCardAssociation`
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base


class ProxyCardAssociation(Base):
    """代理商与充值卡的关联表模型

    用于管理代理商可以销售的充值卡类型
    不使用外键，完全通过业务逻辑进行关联管理
    """

    __tablename__ = "proxy_card_associations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proxy_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ProxyCardAssociation(proxy_user_id={self.proxy_user_id}, card_id={self.card_id})>"
