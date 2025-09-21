# -*- coding: utf-8 -*-
"""
充值卡模块 Pydantic 模型

公开接口：
- `CardCreate`、`CardUpdate`、`CardOut`
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    price: float = Field(..., gt=0)
    is_active: bool = True
    channel_id: int = Field(..., gt=0)


class CardUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)
    price: Optional[float] = Field(default=None, gt=0)
    is_active: Optional[bool] = Field(default=None)
    channel_id: Optional[int] = Field(default=None, gt=0)


class CardOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    is_active: bool
    channel_id: int

    model_config = ConfigDict(from_attributes=True)
