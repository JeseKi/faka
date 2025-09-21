# -*- coding: utf-8 -*-
"""
销售模块 DAO 测试
"""

from sqlalchemy.orm import Session

from src.server.sale.dao import SaleDAO


def test_create_sale(test_db_session: Session):
    """测试创建销售记录"""
    dao = SaleDAO(test_db_session)

    # 创建销售记录
    sale = dao.create(
        user_id=1, card_name="测试充值卡", quantity=2, sale_price=10.0, channel_id=1
    )

    # 验证销售记录已创建
    assert sale.id is not None
    assert sale.user_id == 1
    assert sale.card_name == "测试充值卡"
    assert sale.quantity == 2
    assert sale.sale_price == 10.0
    assert sale.channel_id == 1


def test_get_sale(test_db_session: Session):
    """测试获取销售记录"""
    dao = SaleDAO(test_db_session)

    # 创建销售记录
    created_sale = dao.create(
        user_id=1, card_name="测试充值卡", quantity=1, sale_price=10.0, channel_id=1
    )

    # 获取销售记录
    retrieved_sale = dao.get(created_sale.id)

    # 验证销售记录已正确获取
    assert retrieved_sale is not None
    assert retrieved_sale.id == created_sale.id
    assert retrieved_sale.user_id == 1
    assert retrieved_sale.card_name == "测试充值卡"


def test_list_all_sales(test_db_session: Session):
    """测试获取所有销售记录"""
    dao = SaleDAO(test_db_session)

    # 创建多个销售记录
    dao.create(
        user_id=1, card_name="充值卡1", quantity=1, sale_price=10.0, channel_id=1
    )
    dao.create(
        user_id=2, card_name="充值卡2", quantity=2, sale_price=20.0, channel_id=1
    )

    # 获取所有销售记录
    sales = dao.list_all()

    # 验证销售记录列表
    assert len(sales) >= 2
    assert sales[0].card_name == "充值卡1"
    assert sales[1].card_name == "充值卡2"


def test_get_sales_by_user_id(test_db_session: Session):
    """测试根据用户ID获取销售记录"""
    dao = SaleDAO(test_db_session)

    # 创建属于不同用户的销售记录
    dao.create(
        user_id=1, card_name="用户1的充值卡", quantity=1, sale_price=10.0, channel_id=1
    )
    dao.create(
        user_id=2, card_name="用户2的充值卡", quantity=1, sale_price=15.0, channel_id=1
    )
    dao.create(
        user_id=1,
        card_name="用户1的另一个充值卡",
        quantity=2,
        sale_price=20.0,
        channel_id=1,
    )

    # 获取用户1的销售记录
    user_sales = dao.get_sales_by_user_id(1)

    # 验证用户1的销售记录
    assert len(user_sales) == 2
    for sale in user_sales:
        assert sale.user_id == 1
