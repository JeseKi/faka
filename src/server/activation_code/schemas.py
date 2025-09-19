# -*- coding: utf-8 -*-
"""
卡密模块 Pydantic 模型

公开接口：
- `ActivationCodeCreate`、`ActivationCodeOut`、`ActivationCodeVerify`
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


class CardCodeStatus(str, Enum):
    AVAILABLE = "available"
    CONSUMING = "consuming"
    CONSUMED = "consumed"


class ActivationCodeCreate(BaseModel):
    card_name: str = Field(..., min_length=1, max_length=100)
    count: int = Field(..., gt=0, le=1000)  # 批量生成的数量


class ActivationCodeOut(BaseModel):
    id: int
    card_name: str
    code: str
    status: CardCodeStatus
    created_at: datetime
    used_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ActivationCodeVerify(BaseModel):
    code: str = Field(..., min_length=1, max_length=36)
