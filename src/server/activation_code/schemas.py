# -*- coding: utf-8 -*-
"""
卡密模块 Pydantic 模型

公开接口：
- `ActivationCodeCreate`、`ActivationCodeOut`、`ActivationCodeVerify`、`ActivationCodeCheckResult`
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum


class CardCodeStatus(str, Enum):
    AVAILABLE = "available"
    CONSUMING = "consuming"
    CONSUMED = "consumed"


class ActivationCodeCreate(BaseModel):
    card_id: int = Field(..., gt=0)
    count: int = Field(..., gt=0, le=1000)  # 批量生成的数量
    proxy_user_id: int = Field(..., gt=0, description="代理商用户ID，用于指定卡密归属")


class CardSummary(BaseModel):
    """卡片信息摘要，用于在卡密响应中嵌套显示"""

    id: int
    name: str
    price: float

    model_config = ConfigDict(from_attributes=True)


class ActivationCodeOut(BaseModel):
    id: int
    card_id: int
    card: CardSummary  # 嵌套的卡片信息，包含 id 和 name
    code: str
    status: CardCodeStatus
    created_at: datetime
    used_at: Optional[datetime] = None
    exported: bool

    model_config = ConfigDict(from_attributes=True)


class ActivationCodeVerify(BaseModel):
    code: str = Field(..., min_length=1, max_length=200)


class ActivationCodeCheckResult(BaseModel):
    available: bool
    channel_id: Optional[int] = None


class AvailableActivationCodesResponse(BaseModel):
    """获取可用卡密的响应模型"""

    codes: List[ActivationCodeOut] = Field(..., description="可用卡密列表")
    total_count: int = Field(..., description="总数量")


class ActivationCodeExport(BaseModel):
    """批量导出卡密的请求模型"""

    code_ids: List[int] = Field(..., min_length=1, description="要导出的卡密ID列表")
