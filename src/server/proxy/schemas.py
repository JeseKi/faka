# -*- coding: utf-8 -*-
"""
代理商管理 Pydantic 模型

公开接口：
- `ProxyCardAssociationCreate`、`ProxyCardAssociationOut`
- `ProxyCardLinkRequest`、`ProxyCardUnlinkRequest`
- `ProxyCardListResponse`
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
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


class RevenueQueryParams(BaseModel):
    """销售额查询参数模型"""

    start_date: Optional[datetime] = Field(default=None, description="开始时间（可选）")
    end_date: Optional[datetime] = Field(default=None, description="结束时间（可选）")
    proxy_id: Optional[int] = Field(default=None, description="代理商ID（管理员专用）")
    query: Optional[str] = Field(
        default=None, description="代理商用户名或姓名模糊查询（管理员专用）"
    )


class RevenueResponse(BaseModel):
    """销售额响应模型"""

    proxy_user_id: int
    proxy_username: str
    proxy_name: Optional[str]
    total_revenue: float = Field(..., description="总销售额")
    consumed_count: int = Field(..., description="已消费卡密数量")
    start_date: Optional[datetime] = Field(default=None, description="查询开始时间")
    end_date: Optional[datetime] = Field(default=None, description="查询结束时间")
    query_time_range: str = Field(..., description="查询的时间范围描述")


class MultiRevenueResponse(BaseModel):
    """多代理商销售额响应模型"""

    revenues: List[RevenueResponse] = Field(..., description="代理商销售额列表")
    total_count: int = Field(..., description="匹配到的代理商总数")
