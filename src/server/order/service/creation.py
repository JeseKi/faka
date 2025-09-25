# -*- coding: utf-8 -*-
"""
订单创建服务模块

公开接口：
- verify_activation_code(db, code, channel_id, remarks, card_name)
- create_order(db, activation_code, channel_id, status, remarks, card_name)

内部方法：
- 无

说明：
- 负责订单的创建和验证逻辑，包括卡密验证、订单创建、通知发送等。
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..dao import OrderDAO
from ..models import Order
from ..schemas import OrderStatus, OrderOut
from src.server.activation_code.service import (
    set_code_consuming,
    get_activation_code_by_code,
)
from src.server.card.models import Card
from src.server.auth.dao import UserDAO
from src.server.channel.models import Channel
from src.server.mail_sender.service import send_new_order_notification_email
from src.server.mail_sender.schemas import NewOrderNotificationPayload, MailAddress

if TYPE_CHECKING:
    pass


def verify_activation_code(
    db: Session,
    code: str,
    channel_id: int,
    remarks: str | None = None,
    card_name: str | None = None,
) -> OrderOut:
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

    # 获取价格信息
    pricing = card.price if card else 0.0

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
