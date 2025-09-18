# -*- coding: utf-8 -*-
"""
销售模块服务层

公开接口：
- purchase_card(db, card_name, user_email)
- get_sale_by_activation_code(db, activation_code)
- get_user_sales(db, user_email)
- list_sales(db, limit, offset)
- get_sales_stats(db)

内部方法：
- 无

说明：
- 服务层承载业务逻辑，路由层只做参数校验与装配。
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .dao import SaleDAO
from .models import Sale


def purchase_card(db: Session, card_name: str, user_email: str) -> Sale:
    """购买充值卡"""
    from src.server.card.service import get_card_by_name, get_card_stock
    from src.server.activation_code.service import get_available_activation_code, mark_activation_code_used

    # 验证充值卡是否存在且有库存
    card = get_card_by_name(db, card_name)
    if not card.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该充值卡已下架"
        )

    stock = get_card_stock(db, card_name)
    if stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该充值卡暂时缺货"
        )

    # 获取可用卡密
    activation_code = get_available_activation_code(db, card_name)
    if not activation_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该充值卡暂时缺货"
        )

    # 标记卡密为已使用
    mark_activation_code_used(db, activation_code)

    # 创建销售记录
    dao = SaleDAO(db)
    sale = dao.create(activation_code.code, user_email, card.price)

    return sale


def get_sale_by_activation_code(db: Session, activation_code: str) -> Sale | None:
    """通过卡密获取销售记录"""
    dao = SaleDAO(db)
    return dao.get_by_activation_code(activation_code)


def get_user_sales(db: Session, user_email: str) -> list[Sale]:
    """获取用户的购买记录"""
    dao = SaleDAO(db)
    return dao.get_by_user_email(user_email)


def list_sales(db: Session, limit: int = 100, offset: int = 0) -> list[Sale]:
    """获取销售记录列表"""
    dao = SaleDAO(db)
    return dao.list_all(limit, offset)


def get_sales_stats(db: Session) -> dict:
    """获取销售统计信息"""
    dao = SaleDAO(db)
    total_sales = dao.count_all()
    total_revenue = dao.get_total_revenue()

    return {
        "total_sales": total_sales,
        "total_revenue": total_revenue
    }