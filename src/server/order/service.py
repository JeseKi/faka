# -*- coding: utf-8 -*-
"""
订单模块服务层

公开接口：
- verify_activation_code(db, code, channel_id, remarks)
- create_order(db, activation_code, channel_id, status, remarks)
- get_order(db, order_id)
- list_pending_orders(db)
- list_orders(db, status_filter, limit, offset)
- complete_order(db, order_id, remarks)
- get_order_stats(db)
- get_orders_by_user_id(db, user_id)

内部方法：
- 无

说明：
- 服务层承载业务逻辑，路由层只做参数校验与装配。
"""

from __future__ import annotations
from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .dao import OrderDAO
from .models import Order
from .schemas import OrderStatus
from src.server.activation_code.service import (
    set_code_consuming,
    get_activation_code_by_code,
)
from src.server.card.models import Card
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.auth.dao import UserDAO
from src.server.channel.models import Channel
from src.server.mail_sender.service import send_new_order_notification_email
from src.server.mail_sender.schemas import NewOrderNotificationPayload, MailAddress


def verify_activation_code(
    db: Session,
    code: str,
    channel_id: int,
    remarks: str | None = None,
    card_name: str | None = None,
) -> Order:
    """验证卡密并创建订单"""
    # 首先检查卡密是否存在且可用
    activation_code = get_activation_code_by_code(db, code)
    if not activation_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡密不存在")

    if activation_code.status != "available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="卡密状态不正确"
        )

    # 获取卡密对应的商品
    card = db.query(Card).filter(Card.id == activation_code.card_id).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="卡密对应的商品不存在"
        )

    # 检查商品的渠道是否与传入的渠道ID匹配
    if card.channel_id != channel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="卡密与渠道不匹配"
        )

    # 将卡密状态设置为 consuming
    activation_code = set_code_consuming(db, code)

    # 创建订单，使用传入的充值卡名称或商品的默认名称
    card_name_to_use = card_name if card_name is not None else card.name
    order = create_order(
        db,
        activation_code.code,
        channel_id,
        OrderStatus.PROCESSING,
        remarks,
        card_name_to_use,
    )

    # 发送新订单通知邮件给该渠道的所有员工
    try:
        # 获取渠道信息
        channel = db.query(Channel).filter(Channel.id == channel_id).first()
        if channel:
            # 获取该渠道的所有员工
            user_dao = UserDAO(db)
            staff_members = user_dao.get_staff_by_channel_id(channel_id)

            # 向每个员工发送通知邮件
            for staff in staff_members:
                if staff.email:  # 确保员工有邮箱
                    recipient = MailAddress(email=staff.email, name=staff.name)
                    payload = NewOrderNotificationPayload(
                        recipient=recipient,
                        order_id=order.id,
                        card_name=card.name,
                        activation_code=activation_code.code,
                        created_at=order.created_at,
                        channel_name=channel.name,
                    )
                    # 发送邮件（异步，不阻塞主流程）
                    send_new_order_notification_email(payload)
    except Exception as e:
        # 邮件发送失败不影响订单创建，只记录日志
        import logging

        logging.warning(f"发送新订单通知邮件失败：{e}")

    return order


def create_order(
    db: Session,
    activation_code: str,
    channel_id: int,
    status: OrderStatus = OrderStatus.PROCESSING,
    remarks: str | None = None,
    card_name: str | None = None,
) -> Order:
    """创建订单"""
    dao = OrderDAO(db)
    return dao.create(activation_code, channel_id, status, remarks, card_name)


def get_order(db: Session, order_id: int) -> Order:
    """获取订单"""
    dao = OrderDAO(db)
    order = dao.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return order


def list_pending_orders(db: Session) -> list[Order]:
    """获取所有待处理订单"""
    dao = OrderDAO(db)
    return dao.list_pending()


def list_processing_orders(db: Session, user: User | None = None) -> list[Order]:
    """获取处理中订单"""
    dao = OrderDAO(db)

    # 如果没有用户（管理员）或用户是管理员，返回所有处理中订单
    if not user or user.role == Role.ADMIN:
        return dao.list_processing()

    # 如果是员工，只返回其渠道的处理中订单
    if user.role == Role.STAFF and user.channel_id is not None:
        return dao.list_processing_by_channel(user.channel_id)

    # 如果员工没有渠道ID，返回空列表
    return []


def list_orders(
    db: Session,
    status_filter: OrderStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Order]:
    """获取订单列表"""
    dao = OrderDAO(db)
    return dao.list_all(status_filter, limit, offset)


def complete_order(db: Session, order_id: int, remarks: str | None = None) -> Order:
    """完成订单"""
    from src.server.activation_code.service import (
        set_code_consumed,
        get_activation_code_by_code,
    )

    dao = OrderDAO(db)
    order = dao.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    if order.status == OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="订单已完成"
        )

    # 获取对应的卡密记录
    activation_code = get_activation_code_by_code(db, order.activation_code)
    if not activation_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="关联的卡密不存在"
        )

    # 将卡密状态设置为 consumed
    set_code_consumed(db, activation_code.code)

    return dao.update_status(order, OrderStatus.COMPLETED, remarks)


def get_orders_by_user_id(db: Session, user_id: int) -> List[Order]:
    """获取指定用户的所有订单"""
    dao = OrderDAO(db)
    return dao.get_orders_by_user_id(user_id)


def get_order_stats(db: Session) -> dict:
    """获取订单统计信息"""
    dao = OrderDAO(db)

    pending_count = dao.count_by_status(OrderStatus.PENDING)
    completed_count = dao.count_by_status(OrderStatus.COMPLETED)
    total_count = pending_count + completed_count

    return {
        "total_orders": total_count,
        "pending_orders": pending_count,
        "completed_orders": completed_count,
    }
