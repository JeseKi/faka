# -*- coding: utf-8 -*-
"""
订单查询服务模块

公开接口：
- get_order(db, order_id)
- list_pending_orders(db)
- list_processing_orders(db, user)
- list_orders(db, status_filter, limit, offset)
- get_orders_by_user_id(db, user_id)

内部方法：
- 无

说明：
- 负责订单的查询逻辑，包括单个订单查询、列表查询、按状态查询等。
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..dao import OrderDAO
from ..schemas import OrderStatus, OrderOut
from src.server.auth.models import User
from src.server.auth.schemas import Role

if TYPE_CHECKING:
    pass


def get_order(db: Session, order_id: int) -> OrderOut:
    """获取订单"""
    dao = OrderDAO(db)
    order = dao.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    # 获取价格信息
    pricing = 0.0
    if order.activation_code_obj and order.activation_code_obj.card:
        pricing = order.activation_code_obj.card.price

    # 构造 OrderOut 模型
    return OrderOut(
        id=order.id,
        activation_code=order.activation_code,
        status=OrderStatus(order.status),
        created_at=order.created_at,
        completed_at=order.completed_at,
        remarks=order.remarks,
        channel_id=order.channel_id,
        card_name=order.card_name,
        pricing=pricing,
    )


def list_pending_orders(db: Session) -> list[OrderOut]:
    """获取所有待处理订单"""
    dao = OrderDAO(db)
    orders = dao.list_pending()

    # 构造 OrderOut 模型列表
    order_outs = []
    for order in orders:
        pricing = 0.0
        if order.activation_code_obj and order.activation_code_obj.card:
            pricing = order.activation_code_obj.card.price

        order_out = OrderOut(
            id=order.id,
            activation_code=order.activation_code,
            status=OrderStatus(order.status),
            created_at=order.created_at,
            completed_at=order.completed_at,
            remarks=order.remarks,
            channel_id=order.channel_id,
            card_name=order.card_name,
            pricing=pricing,
        )
        order_outs.append(order_out)

    return order_outs


def list_processing_orders(db: Session, user: User | None = None) -> list[OrderOut]:
    """获取处理中订单"""
    dao = OrderDAO(db)

    # 如果没有用户（管理员）或用户是管理员，返回所有处理中订单
    if not user or user.role == Role.ADMIN:
        orders = dao.list_processing()
    # 如果是员工，只返回其渠道的处理中订单
    elif user.role == Role.STAFF and user.channel_id is not None:
        orders = dao.list_processing_by_channel(user.channel_id)
    # 如果员工没有渠道ID，返回空列表
    else:
        orders = []

    # 构造 OrderOut 模型列表
    order_outs = []
    for order in orders:
        pricing = 0.0
        if order.activation_code_obj and order.activation_code_obj.card:
            pricing = order.activation_code_obj.card.price

        order_out = OrderOut(
            id=order.id,
            activation_code=order.activation_code,
            status=OrderStatus(order.status),
            created_at=order.created_at,
            completed_at=order.completed_at,
            remarks=order.remarks,
            channel_id=order.channel_id,
            card_name=order.card_name,
            pricing=pricing,
        )
        order_outs.append(order_out)

    return order_outs


def list_orders(
    db: Session,
    status_filter: OrderStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[OrderOut]:
    """获取订单列表"""
    dao = OrderDAO(db)
    orders = dao.list_all(status_filter, limit, offset)

    # 构造 OrderOut 模型列表
    order_outs = []
    for order in orders:
        pricing = 0.0
        if order.activation_code_obj and order.activation_code_obj.card:
            pricing = order.activation_code_obj.card.price

        order_out = OrderOut(
            id=order.id,
            activation_code=order.activation_code,
            status=OrderStatus(order.status),
            created_at=order.created_at,
            completed_at=order.completed_at,
            remarks=order.remarks,
            channel_id=order.channel_id,
            card_name=order.card_name,
            pricing=pricing,
        )
        order_outs.append(order_out)

    return order_outs


def get_orders_by_user_id(db: Session, user_id: int) -> List[OrderOut]:
    """获取指定用户的所有订单"""
    dao = OrderDAO(db)
    orders = dao.get_orders_by_user_id(user_id)

    # 构造 OrderOut 模型列表
    order_outs = []
    for order in orders:
        pricing = 0.0
        if order.activation_code_obj and order.activation_code_obj.card:
            pricing = order.activation_code_obj.card.price

        order_out = OrderOut(
            id=order.id,
            activation_code=order.activation_code,
            status=OrderStatus(order.status),
            created_at=order.created_at,
            completed_at=order.completed_at,
            remarks=order.remarks,
            channel_id=order.channel_id,
            card_name=order.card_name,
            pricing=pricing,
        )
        order_outs.append(order_out)

    return order_outs
