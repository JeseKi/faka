# -*- coding: utf-8 -*-
"""
销售记录模块 Pydantic 模型

公开接口：
- `SaleCreate`、`SaleOut`
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SaleCreate(BaseModel):
    card_name: str = Field(..., min_length=1, max_length=100)
    user_email: str = Field(..., min_length=1, max_length=255)


class SaleOut(BaseModel):
    id: int
    activation_code: str
    user_email: str
    sale_price: float
    purchased_at: datetime
    card_name: str  # 添加充值卡名称字段
    quantity: int
    channel_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
