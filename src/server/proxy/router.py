# -*- coding: utf-8 -*-
"""
代理商管理路由

公开接口：
- GET /api/proxy/revenue - 查询代理商销售额
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from src.server.database import get_db
from src.server.utils import get_current_proxy
from ..auth.models import User
from .service import calculate_proxy_revenue
from .schemas import RevenueQueryParams, MultiRevenueResponse

router = APIRouter(prefix="/api/proxy", tags=["代理商管理"])


@router.get("/revenue", response_model=MultiRevenueResponse, summary="查询代理商销售额")
async def get_proxy_revenue(
    start_date: datetime | None = Query(None, description="开始时间（可选）"),
    end_date: datetime | None = Query(None, description="结束时间（可选）"),
    proxy_id: int | None = Query(None, description="代理商ID（管理员专用）"),
    query: str | None = Query(None, description="代理商用户名或姓名模糊查询（管理员专用）"),
    current_user: User = Depends(get_current_proxy),
    db: Session = Depends(get_db),
):
    """查询代理商销售额

    代理商可以查看自己的销售额，管理员可以查询特定代理商的销售额

    Args:
        start_date: 开始时间（可选）
        end_date: 结束时间（可选）
        proxy_id: 代理商ID（管理员专用）
        username: 代理商用户名（管理员专用）
        name: 代理商姓名（管理员专用）
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        RevenueResponse: 销售额统计结果
    """
    try:
        # 构建查询参数
        query_params = RevenueQueryParams(
            start_date=start_date,
            end_date=end_date,
            proxy_id=proxy_id,
            query=query,
        )

        # 计算销售额
        result = calculate_proxy_revenue(db, current_user, query_params)
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"查询销售额时发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询销售额时发生错误",
        )
