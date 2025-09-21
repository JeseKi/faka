# -*- coding: utf-8 -*-
"""
销售模块服务层

公开接口：
- create_sale(db, user_id, card_name, quantity)
- get_sale(db, sale_id)
- list_sales(db, limit, offset)
- get_sales_by_user_id(db, user_id)

内部方法：
- 无

说明：
- 销售模块负责处理用户购买商品的业务逻辑
"""

from __future__ import annotations
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .dao import SaleDAO
from .models import Sale
from src.server.card.service import get_card_stock, get_card_by_name
from src.server.activation_code.service import get_available_activation_code
from src.server.order.service import create_order
from src.server.order.schemas import OrderStatus


def create_sale(db: Session, user_id: int, card_name: str, quantity: int) -> Sale:
    """创建销售记录"""
    # 检查库存是否足够
    stock = get_card_stock(db, card_name)
    if stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"库存不足，当前库存: {stock}"
        )
    
    # 获取商品信息
    card = get_card_by_name(db, card_name)
    
    # 创建销售记录
    dao = SaleDAO(db)
    sale = dao.create(user_id, card_name, quantity, card.price, card.channel_id)
    
    # 为每个购买的数量生成订单
    for _ in range(quantity):
        # 获取一个可用的卡密
        activation_code = get_available_activation_code(db, card_name)
        if not activation_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法获取可用卡密"
            )
        
        # 创建订单，使用商品的渠道ID
        create_order(
            db, 
            activation_code.code, 
            card.channel_id,  # 使用商品的渠道ID
            status=OrderStatus.PENDING
        )
    
    return sale


def get_sale(db: Session, sale_id: int) -> Sale:
    """获取销售记录"""
    dao = SaleDAO(db)
    sale = dao.get(sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="销售记录不存在"
        )
    return sale


def list_sales(db: Session, limit: int = 100, offset: int = 0) -> List[Sale]:
    """获取销售记录列表"""
    dao = SaleDAO(db)
    return dao.list_all(limit, offset)


def get_sales_by_user_id(db: Session, user_id: int) -> List[Sale]:
    """获取指定用户的所有销售记录"""
    dao = SaleDAO(db)
    return dao.get_sales_by_user_id(user_id)
