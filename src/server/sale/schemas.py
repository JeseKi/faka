# -*- coding: utf-8 -*-
"""
销售记录模块 Pydantic 模型

公开接口：
- `SaleCreate`、`SaleOut`
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class SaleCreate(BaseModel):
    card_name: str = Field(..., min_length=1, max_length=100)
    user_email: str = Field(..., min_length=1, max_length=255)


class SaleOut(BaseModel):
    id: int
    activation_code: str
    user_email: str
    sale_price: float
    purchased_at: datetime

    model_config = ConfigDict(from_attributes=True)