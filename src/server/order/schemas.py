# -*- coding: utf-8 -*-
"""
订单模块 Pydantic 模型

公开接口：
- `OrderCreate`、`OrderOut`、`OrderUpdate`、`OrderVerify`
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"


class OrderOut(BaseModel):
    id: int
    activation_code: str
    status: OrderStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    remarks: Optional[str] = None
    channel_id: int
    card_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = Field(default=None)
    remarks: Optional[str] = Field(default=None)


class OrderCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=88)
    channel_id: int = Field(..., gt=0)
    remarks: Optional[str] = Field(default=None)
    card_name: Optional[str] = Field(default=None)
