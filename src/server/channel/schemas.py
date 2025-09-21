# -*- coding: utf-8 -*-
"""
渠道模块 Pydantic 模型

公开接口：
- `ChannelCreate`、`ChannelUpdate`、`ChannelOut`
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ChannelOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)