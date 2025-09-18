# -*- coding: utf-8 -*-
"""
卡密模块服务层测试
"""

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.server.activation_code.models import ActivationCode
from src.server.activation_code.service import (
    create_activation_codes, get_activation_code_by_code,
    get_available_activation_code, mark_activation_code_used,
    list_activation_codes_by_card, count_activation_codes_by_card,
    delete_activation_codes_by_card, verify_and_use_code
)


def test_create_activation_codes(test_db_session: Session):
    """测试批量创建卡密"""
    codes = create_activation_codes(test_db_session, "月度会员", 3)

    assert len(codes) == 3
    for code in codes:
        assert code.card_name == "月度会员"
        assert code.is_used == False
        assert code.used_at is None


def test_get_activation_code_by_code(test_db_session: Session):
    """测试通过卡密获取记录"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "季度会员", 1)
    code_value = codes[0].code

    # 获取存在的卡密
    retrieved_code = get_activation_code_by_code(test_db_session, code_value)
    assert retrieved_code is not None
    assert retrieved_code.code == code_value

    # 获取不存在的卡密
    retrieved_code = get_activation_code_by_code(test_db_session, "non-existent")
    assert retrieved_code is None


def test_get_available_activation_code(test_db_session: Session):
    """测试获取可用卡密"""
    # 创建测试数据
    create_activation_codes(test_db_session, "年度会员", 2)

    # 获取可用卡密
    available_code = get_available_activation_code(test_db_session, "年度会员")
    assert available_code is not None
    assert available_code.is_used == False


def test_mark_activation_code_used(test_db_session: Session):
    """测试标记卡密为已使用"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "测试卡", 1)
    code = codes[0]

    assert code.is_used == False

    # 标记为已使用
    updated_code = mark_activation_code_used(test_db_session, code)

    assert updated_code.is_used == True
    assert updated_code.used_at is not None


def test_list_activation_codes_by_card(test_db_session: Session):
    """测试列出指定充值卡的卡密"""
    # 创建测试数据
    create_activation_codes(test_db_session, "卡1", 2)

    # 只获取未使用的
    unused_codes = list_activation_codes_by_card(test_db_session, "卡1", include_used=False)
    assert len(unused_codes) == 2

    # 获取所有
    all_codes = list_activation_codes_by_card(test_db_session, "卡1", include_used=True)
    assert len(all_codes) == 2


def test_count_activation_codes_by_card(test_db_session: Session):
    """测试统计卡密数量"""
    # 创建测试数据
    create_activation_codes(test_db_session, "统计测试", 3)

    # 统计未使用的
    count = count_activation_codes_by_card(test_db_session, "统计测试", only_unused=True)
    assert count == 3

    # 统计所有
    count = count_activation_codes_by_card(test_db_session, "统计测试", only_unused=False)
    assert count == 3


def test_delete_activation_codes_by_card(test_db_session: Session):
    """测试删除指定充值卡的所有卡密"""
    # 创建测试数据
    create_activation_codes(test_db_session, "待删除", 2)
    create_activation_codes(test_db_session, "保留", 1)

    # 删除指定充值卡的卡密
    deleted_count = delete_activation_codes_by_card(test_db_session, "待删除")
    assert deleted_count == 2

    # 验证已删除
    count = count_activation_codes_by_card(test_db_session, "待删除", only_unused=False)
    assert count == 0

    # 验证其他卡密未受影响
    count = count_activation_codes_by_card(test_db_session, "保留", only_unused=False)
    assert count == 1


def test_verify_and_use_code(test_db_session: Session):
    """测试验证并使用卡密"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "验证测试", 1)
    code_value = codes[0].code

    # 验证并使用卡密
    used_code = verify_and_use_code(test_db_session, code_value)

    assert used_code.code == code_value
    assert used_code.is_used == True
    assert used_code.used_at is not None

    # 再次验证同一个卡密，应该失败
    with pytest.raises(HTTPException) as exc_info:
        verify_and_use_code(test_db_session, code_value)

    assert exc_info.value.status_code == 400
    assert "已被使用" in exc_info.value.detail

    # 验证不存在的卡密
    with pytest.raises(HTTPException) as exc_info:
        verify_and_use_code(test_db_session, "non-existent-code")

    assert exc_info.value.status_code == 404
    assert "不存在" in exc_info.value.detail