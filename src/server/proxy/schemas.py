# -*- coding: utf-8 -*-
"""
代理商管理 Pydantic 模型

公开接口：
- `ProxyCardAssociationCreate`、`ProxyCardAssociationOut`
- `ProxyCardLinkRequest`、`ProxyCardUnlinkRequest`
- `ProxyCardListResponse`
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime


class ProxyCardAssociationCreate(BaseModel):
    """创建代理商与充值卡关联的请求模型"""

    proxy_user_id: int = Field(..., description="代理商用户ID")
    card_id: int = Field(..., description="充值卡ID")


class ProxyCardAssociationOut(BaseModel):
    """代理商与充值卡关联的响应模型"""

    id: int
    proxy_user_id: int
    card_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProxyCardLinkRequest(BaseModel):
    """绑定代理商与充值卡的请求模型"""

    proxy_user_id: int = Field(..., description="代理商用户ID")
    card_ids: List[int] = Field(..., description="要绑定的充值卡ID列表")


class ProxyCardUnlinkRequest(BaseModel):
    """解绑代理商与充值卡的请求模型"""

    proxy_user_id: int = Field(..., description="代理商用户ID")
    card_ids: List[int] = Field(..., description="要解绑的充值卡ID列表")


class ProxyCardListResponse(BaseModel):
    """代理商绑定的充值卡列表响应模型"""

    proxy_user_id: int
    cards: List[dict] = Field(..., description="绑定的充值卡信息列表")
    total_count: int = Field(..., description="绑定卡数量")
