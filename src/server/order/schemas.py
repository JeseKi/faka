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


class OrderCreate(BaseModel):
    activation_code: str = Field(..., min_length=1, max_length=36)


class OrderOut(BaseModel):
    id: int
    activation_code: str
    status: OrderStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = Field(None)
    remarks: Optional[str] = Field(None, max_length=1000)


class OrderVerify(BaseModel):
    code: str = Field(..., min_length=1, max_length=36)
