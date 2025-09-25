# -*- coding: utf-8 -*-
"""
代理商销售额统计服务

公开接口：
- `calculate_proxy_revenue`

内部方法：
- `_calculate_single_proxy_revenue`
"""

from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models import ProxyCardAssociation
from ..schemas import RevenueQueryParams, RevenueResponse, MultiRevenueResponse
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.activation_code.models import ActivationCode, CardCodeStatus


def calculate_proxy_revenue(
    db: Session, current_user: User, query_params: RevenueQueryParams
) -> MultiRevenueResponse:
    """计算代理商销售额

    代理商可以查看自己的销售额，管理员可以查询特定代理商的销售额

    Args:
        db: 数据库会话
        current_user: 当前登录用户
        query_params: 查询参数

    Returns:
        MultiRevenueResponse: 多个代理商的销售额统计结果

    Raises:
        ValueError: 当用户权限不足时
    """
    # 验证用户权限
    target_proxies: List[User] = []
    if current_user.role == Role.PROXY:
        # 代理商只能查看自己的销售额
        target_proxies = [current_user]
    elif current_user.role == Role.ADMIN:
        # 管理员可以查询特定代理商
        if query_params.proxy_id:
            target_proxy = (
                db.query(User).filter(User.id == query_params.proxy_id).first()
            )
            if target_proxy:
                target_proxies = [target_proxy]
        elif query_params.query:
            # 使用模糊查询同时匹配用户名和姓名
            target_proxies = (
                db.query(User)
                .filter(
                    User.role == Role.PROXY,
                    or_(
                        User.username.ilike(f"%{query_params.query}%"),
                        User.name.ilike(f"%{query_params.query}%"),
                    ),
                )
                .all()
            )
        else:
            raise ValueError("管理员查询必须指定代理商ID或查询关键词")

        # 验证所有目标用户都是代理商
        for proxy in target_proxies:
            if proxy.role != Role.PROXY:
                raise ValueError("指定的用户不是代理商")
    else:
        raise ValueError("只有代理商和管理员才能查询销售额")

    if not target_proxies:
        # 没有找到任何代理商
        return MultiRevenueResponse(revenues=[], total_count=0)

    # 为每个代理商计算销售额
    revenues = []
    for target_proxy in target_proxies:
        revenue_data = _calculate_single_proxy_revenue(db, target_proxy, query_params)
        revenues.append(revenue_data)

    return MultiRevenueResponse(revenues=revenues, total_count=len(revenues))


def _calculate_single_proxy_revenue(
    db: Session, target_proxy: User, query_params: RevenueQueryParams
) -> RevenueResponse:
    """计算单个代理商的销售额

    Args:
        db: 数据库会话
        target_proxy: 目标代理商用户
        query_params: 查询参数

    Returns:
        RevenueResponse: 单个代理商的销售额统计结果
    """
    target_proxy_id = target_proxy.id

    # 获取代理商绑定的所有充值卡ID
    associations = (
        db.query(ProxyCardAssociation)
        .filter(ProxyCardAssociation.proxy_user_id == target_proxy_id)
        .all()
    )

    if not associations:
        # 代理商没有绑定任何充值卡，返回零销售额
        return RevenueResponse(
            proxy_user_id=target_proxy_id,
            proxy_username=target_proxy.username,
            proxy_name=target_proxy.name,
            total_revenue=0.0,
            consumed_count=0,
            start_date=query_params.start_date,
            end_date=query_params.end_date,
            query_time_range="无绑定卡密",
        )

    card_ids = [assoc.card_id for assoc in associations]

    # 构建查询条件
    query = db.query(ActivationCode).filter(
        ActivationCode.card_id.in_(card_ids),
        ActivationCode.status == CardCodeStatus.CONSUMED,
        ActivationCode.proxy_user_id == target_proxy_id,
    )

    # 添加时间筛选
    time_range_desc = "全部时间"
    if query_params.start_date:
        query = query.filter(ActivationCode.used_at >= query_params.start_date)
        time_range_desc = (
            f"从 {query_params.start_date.strftime('%Y-%m-%d %H:%M:%S')} 开始"
        )
    if query_params.end_date:
        query = query.filter(ActivationCode.used_at <= query_params.end_date)
        if query_params.start_date:
            time_range_desc = f"{query_params.start_date.strftime('%Y-%m-%d %H:%M:%S')} 至 {query_params.end_date.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            time_range_desc = (
                f"至 {query_params.end_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )

    # 获取已消费的卡密
    consumed_codes = query.all()
    consumed_count = len(consumed_codes)

    if consumed_count == 0:
        return RevenueResponse(
            proxy_user_id=target_proxy_id,
            proxy_username=target_proxy.username,
            proxy_name=target_proxy.name,
            total_revenue=0.0,
            consumed_count=0,
            start_date=query_params.start_date,
            end_date=query_params.end_date,
            query_time_range=time_range_desc,
        )

    # 直接通过已消费的卡密计算总销售额
    total_revenue = 0.0
    for consumed_code in consumed_codes:
        # 通过 ActivationCode 的 card 关联获取价格
        if consumed_code.card and consumed_code.card.price:
            total_revenue += consumed_code.card.price
    return RevenueResponse(
        proxy_user_id=target_proxy_id,
        proxy_username=target_proxy.username,
        proxy_name=target_proxy.name,
        total_revenue=total_revenue,
        consumed_count=consumed_count,
        start_date=query_params.start_date,
        end_date=query_params.end_date,
        query_time_range=time_range_desc,
    )
