# -*- coding: utf-8 -*-
"""
卡密模块DAO层测试
"""

import pytest
from sqlalchemy.orm import Session

from src.server.activation_code.dao import ActivationCodeDAO
from src.server.activation_code.models import ActivationCode


def test_activation_code_dao_create_batch(test_db_session: Session):
    """测试批量创建卡密"""
    dao = ActivationCodeDAO(test_db_session)

    # 批量创建
    codes = dao.create_batch("月度会员", 3)

    assert len(codes) == 3
    for code in codes:
        assert code.card_name == "月度会员"
        assert code.is_used == False
        assert code.used_at is None
        assert code.code is not None
        assert len(code.code) == 36  # UUID 长度


def test_activation_code_dao_get_by_code(test_db_session: Session):
    """测试通过卡密获取记录"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes = dao.create_batch("季度会员", 1)
    code_value = codes[0].code

    # 获取存在的卡密
    retrieved_code = dao.get_by_code(code_value)
    assert retrieved_code is not None
    assert retrieved_code.code == code_value
    assert retrieved_code.card_name == "季度会员"

    # 获取不存在的卡密
    retrieved_code = dao.get_by_code("non-existent-code")
    assert retrieved_code is None


def test_activation_code_dao_get_available_by_card_name(test_db_session: Session):
    """测试获取可用卡密"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes = dao.create_batch("年度会员", 2)

    # 获取可用卡密
    available_code = dao.get_available_by_card_name("年度会员")
    assert available_code is not None
    assert available_code.card_name == "年度会员"
    assert available_code.is_used == False

    # 标记为已使用
    dao.mark_as_used(available_code)

    # 再次获取，应该返回另一个
    another_code = dao.get_available_by_card_name("年度会员")
    assert another_code is not None
    assert another_code.id != available_code.id

    # 标记第二个也为已使用
    dao.mark_as_used(another_code)

    # 应该没有可用卡密了
    no_code = dao.get_available_by_card_name("年度会员")
    assert no_code is None


def test_activation_code_dao_mark_as_used(test_db_session: Session):
    """测试标记卡密为已使用"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes = dao.create_batch("测试卡", 1)
    code = codes[0]

    assert code.is_used == False
    assert code.used_at is None

    # 标记为已使用
    updated_code = dao.mark_as_used(code)

    assert updated_code.is_used == True
    assert updated_code.used_at is not None


def test_activation_code_dao_list_by_card_name(test_db_session: Session):
    """测试列出指定充值卡的卡密"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes1 = dao.create_batch("卡1", 2)
    codes2 = dao.create_batch("卡2", 1)

    # 只获取未使用的
    unused_codes = dao.list_by_card_name("卡1", include_used=False)
    assert len(unused_codes) == 2
    assert all(not code.is_used for code in unused_codes)

    # 标记一个为已使用
    dao.mark_as_used(codes1[0])

    # 获取所有卡密
    all_codes = dao.list_by_card_name("卡1", include_used=True)
    assert len(all_codes) == 2

    # 只获取未使用的
    unused_codes = dao.list_by_card_name("卡1", include_used=False)
    assert len(unused_codes) == 1


def test_activation_code_dao_count_by_card_name(test_db_session: Session):
    """测试统计卡密数量"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    codes = dao.create_batch("统计测试", 3)

    # 统计未使用的
    count = dao.count_by_card_name("统计测试", only_unused=True)
    assert count == 3

    # 标记一个为已使用
    dao.mark_as_used(codes[0])

    # 再次统计
    count = dao.count_by_card_name("统计测试", only_unused=True)
    assert count == 2

    # 统计所有
    count = dao.count_by_card_name("统计测试", only_unused=False)
    assert count == 3


def test_activation_code_dao_delete_by_card_name(test_db_session: Session):
    """测试删除指定充值卡的所有卡密"""
    dao = ActivationCodeDAO(test_db_session)

    # 创建测试数据
    dao.create_batch("待删除", 2)
    dao.create_batch("保留", 1)

    # 删除指定充值卡的卡密
    deleted_count = dao.delete_by_card_name("待删除")
    assert deleted_count == 2

    # 验证已删除
    count = dao.count_by_card_name("待删除", only_unused=False)
    assert count == 0

    # 验证其他卡密未受影响
    count = dao.count_by_card_name("保留", only_unused=False)
    assert count == 1