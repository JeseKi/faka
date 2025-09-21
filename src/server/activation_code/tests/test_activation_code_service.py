# -*- coding: utf-8 -*-
"""
卡密模块服务层测试
"""

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.server.activation_code.service import (
    create_activation_codes,
    get_activation_code_by_code,
    get_available_activation_code,
    list_activation_codes_by_card,
    count_activation_codes_by_card,
    delete_activation_codes_by_card,
    set_code_consuming,
    set_code_consumed,
    is_code_available,
    is_code_available_for_user,
)
from src.server.activation_code.models import CardCodeStatus
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.card.models import Card
from src.server.channel.models import Channel


@pytest.fixture
def setup_test_data(test_db_session: Session):
    """设置测试数据：创建渠道和充值卡"""
    # 创建测试渠道
    channel = Channel(name="测试渠道", description="用于测试的渠道")
    test_db_session.add(channel)
    test_db_session.commit()
    test_db_session.refresh(channel)
    
    # 创建测试充值卡
    cards_data = [
        ("月度会员", "月度会员充值卡"),
        ("季度会员", "季度会员充值卡"),
        ("年度会员", "年度会员充值卡"),
        ("卡1", "卡1充值卡"),
        ("统计测试", "统计测试充值卡"),
        ("待删除", "待删除充值卡"),
        ("消费测试", "消费测试充值卡"),
        ("可用性测试", "可用性测试充值卡"),
        ("渠道测试卡", "渠道测试充值卡"),
        ("不存在的商品", "不存在的商品充值卡"),
        ("保留", "保留充值卡"),
    ]
    
    cards = []
    for name, description in cards_data:
        card = Card(
            name=name,
            description=description,
            price=10.0,
            is_active=True,
            channel_id=channel.id,
        )
        test_db_session.add(card)
        cards.append(card)
    
    test_db_session.commit()
    for card in cards:
        test_db_session.refresh(card)
    
    return channel, cards


def test_create_activation_codes(test_db_session: Session, setup_test_data):
    """测试批量创建卡密"""
    codes = create_activation_codes(test_db_session, "月度会员", 3)

    assert len(codes) == 3
    for code in codes:
        assert code.card_name == "月度会员"
        assert code.status == CardCodeStatus.AVAILABLE
        assert code.used_at is None


def test_get_activation_code_by_code(test_db_session: Session, setup_test_data):
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


def test_get_available_activation_code(test_db_session: Session, setup_test_data):
    """测试获取可用卡密"""
    # 创建测试数据
    create_activation_codes(test_db_session, "年度会员", 2)

    # 获取可用卡密
    available_code = get_available_activation_code(test_db_session, "年度会员")
    assert available_code is not None
    assert available_code.status == CardCodeStatus.AVAILABLE


def test_list_activation_codes_by_card(test_db_session: Session, setup_test_data):
    """测试列出指定充值卡的卡密"""
    # 创建测试数据
    create_activation_codes(test_db_session, "卡1", 2)

    # 只获取未使用的 (available 状态)
    unused_codes = list_activation_codes_by_card(
        test_db_session, "卡1", include_used=False
    )
    assert len(unused_codes) == 2

    # 获取所有
    all_codes = list_activation_codes_by_card(test_db_session, "卡1", include_used=True)
    assert len(all_codes) == 2


def test_count_activation_codes_by_card(test_db_session: Session, setup_test_data):
    """测试统计卡密数量"""
    # 创建测试数据
    create_activation_codes(test_db_session, "统计测试", 3)

    # 统计未使用的 (available 状态)
    count = count_activation_codes_by_card(
        test_db_session, "统计测试", only_unused=True
    )
    assert count == 3

    # 统计所有
    count = count_activation_codes_by_card(
        test_db_session, "统计测试", only_unused=False
    )
    assert count == 3


def test_delete_activation_codes_by_card(test_db_session: Session, setup_test_data):
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


def test_set_code_consuming_success(test_db_session: Session, setup_test_data):
    """测试成功设置卡密为 consuming 状态"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "消费测试", 1)
    code_value = codes[0].code

    # 设置为 consuming 状态
    consuming_code = set_code_consuming(test_db_session, code_value)

    assert consuming_code.status == CardCodeStatus.CONSUMING
    assert consuming_code.used_at is None


def test_set_code_consuming_not_found(test_db_session: Session, setup_test_data):
    """测试对不存在的卡密调用 consuming 接口失败"""
    with pytest.raises(HTTPException) as exc_info:
        set_code_consuming(test_db_session, "non-existent-code")

    assert exc_info.value.status_code == 404
    assert "不存在" in exc_info.value.detail


def test_set_code_consuming_invalid_status(test_db_session: Session, setup_test_data):
    """测试对非 available 状态的卡密调用 consuming 接口失败"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "消费测试", 1)
    code_value = codes[0].code

    # 先将卡密状态设置为 consuming
    set_code_consuming(test_db_session, code_value)

    # 再次调用 consuming API，应该失败
    with pytest.raises(HTTPException) as exc_info:
        set_code_consuming(test_db_session, code_value)

    assert exc_info.value.status_code == 400
    assert "状态不正确" in exc_info.value.detail


def test_set_code_consumed_success(test_db_session: Session, setup_test_data):
    """测试成功设置卡密为 consumed 状态"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "消费测试", 1)
    code_value = codes[0].code

    # 先设置为 consuming 状态
    set_code_consuming(test_db_session, code_value)

    # 设置为 consumed 状态
    consumed_code = set_code_consumed(test_db_session, code_value)

    assert consumed_code.status == CardCodeStatus.CONSUMED
    assert consumed_code.used_at is not None


def test_set_code_consumed_not_found(test_db_session: Session, setup_test_data):
    """测试对不存在的卡密调用 consumed 接口失败"""
    with pytest.raises(HTTPException) as exc_info:
        set_code_consumed(test_db_session, "non-existent-code")

    assert exc_info.value.status_code == 404
    assert "不存在" in exc_info.value.detail


def test_set_code_consumed_invalid_status(test_db_session: Session, setup_test_data):
    """测试对非 consuming 状态的卡密调用 consumed 接口失败"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "消费测试", 1)
    code_value = codes[0].code

    # 直接调用 consumed API，应该失败（因为状态是 available）
    with pytest.raises(HTTPException) as exc_info:
        set_code_consumed(test_db_session, code_value)

    assert exc_info.value.status_code == 400
    assert "状态不正确" in exc_info.value.detail


def test_is_code_available_success(test_db_session: Session, setup_test_data):
    """测试成功检查卡密是否可用"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "可用性测试", 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    result = is_code_available(test_db_session, code_value)
    assert result.available is True


def test_is_code_available_not_found(test_db_session: Session, setup_test_data):
    """测试检查不存在的卡密"""
    # 检查不存在的卡密
    result = is_code_available(test_db_session, "non-existent-code")
    assert result.available is False


def test_is_code_available_consumed(test_db_session: Session, setup_test_data):
    """测试检查已消费的卡密"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "可用性测试", 1)
    code_value = codes[0].code

    # 将卡密状态设置为 consuming
    set_code_consuming(test_db_session, code_value)

    # 检查卡密是否可用
    result = is_code_available(test_db_session, code_value)
    assert result.available is False


def test_is_code_available_consuming(test_db_session: Session, setup_test_data):
    """测试检查正在消费的卡密"""
    # 创建测试数据
    codes = create_activation_codes(test_db_session, "可用性测试", 1)
    code_value = codes[0].code

    # 将卡密状态设置为 consuming
    set_code_consuming(test_db_session, code_value)
    set_code_consumed(test_db_session, code_value)

    # 检查卡密是否可用
    result = is_code_available(test_db_session, code_value)
    assert result.available is False


def test_is_code_available_for_user_success(test_db_session: Session, setup_test_data):
    """测试 STAFF 用户检查卡密是否可用且渠道匹配"""
    # 获取已创建的渠道
    channel = test_db_session.query(Channel).first()

    # 创建 STAFF 用户
    assert channel is not None
    staff_user = User(
        username="staff_user",
        email="staff@example.com",
        role=Role.STAFF,
        channel_id=channel.id,
    )
    staff_user.set_password("password")
    test_db_session.add(staff_user)
    test_db_session.commit()
    test_db_session.refresh(staff_user)

    # 创建卡密
    codes = create_activation_codes(test_db_session, "渠道测试卡", 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    assert is_code_available_for_user(test_db_session, code_value, staff_user) is True


def test_is_code_available_for_user_channel_mismatch(test_db_session: Session, setup_test_data):
    """测试 STAFF 用户检查卡密是否可用但渠道不匹配"""
    # 创建第二个渠道
    _ = test_db_session.query(Channel).first()
    channel2 = Channel(name="测试渠道2", description="用于测试的渠道2")
    test_db_session.add(channel2)
    test_db_session.commit()
    test_db_session.refresh(channel2)

    # 创建 STAFF 用户并关联到渠道2
    staff_user = User(
        username="staff_user",
        email="staff@example.com",
        role=Role.STAFF,
        channel_id=channel2.id,
    )
    staff_user.set_password("password")
    test_db_session.add(staff_user)
    test_db_session.commit()
    test_db_session.refresh(staff_user)

    # 创建卡密
    codes = create_activation_codes(test_db_session, "渠道测试卡", 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    assert is_code_available_for_user(test_db_session, code_value, staff_user) is False


def test_is_code_available_for_user_admin_user(test_db_session: Session, setup_test_data):
    """测试 ADMIN 用户检查卡密是否可用（不考虑渠道）"""
    # 获取已创建的渠道
    _ = test_db_session.query(Channel).first()

    # 创建 ADMIN 用户
    admin_user = User(username="admin_user", email="admin@example.com", role=Role.ADMIN)
    admin_user.set_password("password")
    test_db_session.add(admin_user)
    test_db_session.commit()
    test_db_session.refresh(admin_user)

    # 创建卡密
    codes = create_activation_codes(test_db_session, "渠道测试卡", 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    assert is_code_available_for_user(test_db_session, code_value, admin_user) is True


def test_is_code_available_for_user_user_role(test_db_session: Session, setup_test_data):
    """测试 USER 角色检查卡密是否可用（不考虑渠道）"""
    # 创建 USER 用户
    user = User(username="user", email="user@example.com", role=Role.USER)
    user.set_password("password")
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)

    # 创建卡密
    codes = create_activation_codes(test_db_session, "渠道测试卡", 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    assert is_code_available_for_user(test_db_session, code_value, user) is True


def test_is_code_available_for_user_card_not_found(test_db_session: Session, setup_test_data):
    """测试卡密对应的商品不存在"""
    # 获取已创建的渠道
    channel = test_db_session.query(Channel).first()

    # 创建 STAFF 用户
    assert channel is not None
    staff_user = User(
        username="staff_user",
        email="staff@example.com",
        role=Role.STAFF,
        channel_id=channel.id,
    )
    staff_user.set_password("password")
    test_db_session.add(staff_user)
    test_db_session.commit()
    test_db_session.refresh(staff_user)

    # 手动创建一个卡密，但对应的商品不存在
    from src.server.activation_code.models import ActivationCode, CardCodeStatus
    from datetime import datetime, timezone
    import uuid
    from src.server.crypto.service import encrypt
    
    # 生成加密的卡密代码
    original_uuid = str(uuid.uuid4())
    data_to_encrypt = f"{original_uuid}:测试渠道"
    encrypted_code = encrypt(data_to_encrypt)
    
    # 创建卡密记录（关联到不存在的商品）
    activation_code = ActivationCode(
        card_name="真正不存在的商品",  # 这个商品在setup_test_data中未创建
        code=encrypted_code,
        is_sold=False,
        status=CardCodeStatus.AVAILABLE,
        created_at=datetime.now(timezone.utc),
    )
    test_db_session.add(activation_code)
    test_db_session.commit()
    test_db_session.refresh(activation_code)
    
    code_value = activation_code.code

    # 检查卡密是否可用，应该返回False，因为商品不存在
    result = is_code_available_for_user(test_db_session, code_value, staff_user)
    assert result is False
