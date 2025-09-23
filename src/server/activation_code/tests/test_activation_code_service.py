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
    get_available_activation_codes,
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
    _, cards = setup_test_data
    card_id = cards[0].id  # "月度会员" 的 ID
    codes = create_activation_codes(test_db_session, card_id, 3)

    assert len(codes) == 3
    for code in codes:
        assert code.card_id == card_id
        assert code.status == CardCodeStatus.AVAILABLE
        assert code.used_at is None
        assert code.proxy_user_id is None  # 默认情况下应该是 None
        assert code.exported is False  # 默认情况下应该是 False


def test_create_activation_codes_with_proxy_user_id(
    test_db_session: Session, setup_test_data
):
    """测试批量创建卡密时指定代理商ID"""
    # 创建代理商用户
    proxy_user = User(
        username="proxy_test", email="proxy_test@example.com", role=Role.PROXY
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    _, cards = setup_test_data
    card_id = cards[0].id  # "月度会员" 的 ID
    codes = create_activation_codes(test_db_session, card_id, 2, proxy_user.id)

    assert len(codes) == 2
    for code in codes:
        assert code.card_id == card_id
        assert code.status == CardCodeStatus.AVAILABLE
        assert code.used_at is None
        assert code.proxy_user_id == proxy_user.id  # 应该等于指定的代理商ID
        assert code.exported is False  # 默认情况下应该是 False


def test_get_activation_code_by_code(test_db_session: Session, setup_test_data):
    """测试通过卡密获取记录"""
    _, cards = setup_test_data
    card_id = cards[1].id  # "季度会员" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
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
    _, cards = setup_test_data
    card_id = cards[2].id  # "年度会员" 的 ID
    # 创建测试数据
    create_activation_codes(test_db_session, card_id, 2)

    # 获取可用卡密
    available_code = get_available_activation_code(test_db_session, card_id)
    assert available_code is not None
    assert available_code.status == CardCodeStatus.AVAILABLE


def test_list_activation_codes_by_card(test_db_session: Session, setup_test_data):
    """测试列出指定充值卡的卡密"""
    _, cards = setup_test_data
    card_id = cards[3].id  # "卡1" 的 ID
    # 创建测试数据
    create_activation_codes(test_db_session, card_id, 2)

    # 只获取未使用的 (available 状态)
    unused_codes = list_activation_codes_by_card(
        test_db_session, card_id, include_used=False
    )
    assert len(unused_codes) == 2

    # 获取所有
    all_codes = list_activation_codes_by_card(
        test_db_session, card_id, include_used=True
    )
    assert len(all_codes) == 2


def test_count_activation_codes_by_card(test_db_session: Session, setup_test_data):
    """测试统计卡密数量"""
    _, cards = setup_test_data
    card_id = cards[4].id  # "统计测试" 的 ID
    # 创建测试数据
    create_activation_codes(test_db_session, card_id, 3)

    # 统计未使用的 (available 状态)
    count = count_activation_codes_by_card(test_db_session, card_id, only_unused=True)
    assert count == 3

    # 统计所有
    count = count_activation_codes_by_card(test_db_session, card_id, only_unused=False)
    assert count == 3


def test_delete_activation_codes_by_card(test_db_session: Session, setup_test_data):
    """测试删除指定充值卡的所有卡密"""
    _, cards = setup_test_data
    card_id_to_delete = cards[5].id  # "待删除" 的 ID
    card_id_to_keep = cards[10].id  # "保留" 的 ID
    # 创建测试数据
    create_activation_codes(test_db_session, card_id_to_delete, 2)
    create_activation_codes(test_db_session, card_id_to_keep, 1)

    # 删除指定充值卡的卡密
    deleted_count = delete_activation_codes_by_card(test_db_session, card_id_to_delete)
    assert deleted_count == 2

    # 验证已删除
    count = count_activation_codes_by_card(
        test_db_session, card_id_to_delete, only_unused=False
    )
    assert count == 0

    # 验证其他卡密未受影响
    count = count_activation_codes_by_card(
        test_db_session, card_id_to_keep, only_unused=False
    )
    assert count == 1


def test_set_code_consuming_success(test_db_session: Session, setup_test_data):
    """测试成功设置卡密为 consuming 状态"""
    _, cards = setup_test_data
    card_id = cards[6].id  # "消费测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
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
    _, cards = setup_test_data
    card_id = cards[6].id  # "消费测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
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
    _, cards = setup_test_data
    card_id = cards[6].id  # "消费测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
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
    _, cards = setup_test_data
    card_id = cards[6].id  # "消费测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
    code_value = codes[0].code

    # 直接调用 consumed API，应该失败（因为状态是 available）
    with pytest.raises(HTTPException) as exc_info:
        set_code_consumed(test_db_session, code_value)

    assert exc_info.value.status_code == 400
    assert "状态不正确" in exc_info.value.detail


def test_is_code_available_success(test_db_session: Session, setup_test_data):
    """测试成功检查卡密是否可用"""
    _, cards = setup_test_data
    card_id = cards[7].id  # "可用性测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
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
    _, cards = setup_test_data
    card_id = cards[7].id  # "可用性测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
    code_value = codes[0].code

    # 将卡密状态设置为 consuming
    set_code_consuming(test_db_session, code_value)

    # 检查卡密是否可用
    result = is_code_available(test_db_session, code_value)
    assert result.available is False


def test_is_code_available_consuming(test_db_session: Session, setup_test_data):
    """测试检查正在消费的卡密"""
    _, cards = setup_test_data
    card_id = cards[7].id  # "可用性测试" 的 ID
    # 创建测试数据
    codes = create_activation_codes(test_db_session, card_id, 1)
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
    _, cards = setup_test_data
    card_id = cards[8].id  # "渠道测试卡" 的 ID
    codes = create_activation_codes(test_db_session, card_id, 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    assert is_code_available_for_user(test_db_session, code_value, staff_user) is True


def test_is_code_available_for_user_channel_mismatch(
    test_db_session: Session, setup_test_data
):
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
    _, cards = setup_test_data
    card_id = cards[8].id  # "渠道测试卡" 的 ID
    codes = create_activation_codes(test_db_session, card_id, 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    assert is_code_available_for_user(test_db_session, code_value, staff_user) is False


def test_is_code_available_for_user_admin_user(
    test_db_session: Session, setup_test_data
):
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
    _, cards = setup_test_data
    card_id = cards[8].id  # "渠道测试卡" 的 ID
    codes = create_activation_codes(test_db_session, card_id, 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    assert is_code_available_for_user(test_db_session, code_value, admin_user) is True


def test_is_code_available_for_user_user_role(
    test_db_session: Session, setup_test_data
):
    """测试 USER 角色检查卡密是否可用（不考虑渠道）"""
    # 创建 USER 用户
    user = User(username="user", email="user@example.com", role=Role.USER)
    user.set_password("password")
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)

    # 创建卡密
    _, cards = setup_test_data
    card_id = cards[8].id  # "渠道测试卡" 的 ID
    codes = create_activation_codes(test_db_session, card_id, 1)
    code_value = codes[0].code

    # 检查卡密是否可用
    assert is_code_available_for_user(test_db_session, code_value, user) is True


def test_is_code_available_for_user_card_not_found(
    test_db_session: Session, setup_test_data
):
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
        card_id=999999,  # 这个商品在setup_test_data中未创建
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


def test_get_available_activation_codes_admin_all(
    test_db_session: Session, setup_test_data
):
    """测试管理员获取所有可用卡密"""
    # 创建管理员用户
    admin_user = User(
        username="admin_test", email="admin_test@example.com", role=Role.ADMIN
    )
    admin_user.set_password("password123")
    test_db_session.add(admin_user)
    test_db_session.commit()
    test_db_session.refresh(admin_user)

    # 创建测试卡密
    _, cards = setup_test_data
    card_id = cards[0].id
    _ = create_activation_codes(test_db_session, card_id, 3)

    # 管理员获取所有可用卡密
    available_codes, total_count = get_available_activation_codes(
        test_db_session, admin_user
    )

    assert len(available_codes) == 3
    assert total_count == 3
    for code in available_codes:
        assert code.status == CardCodeStatus.AVAILABLE


def test_get_available_activation_codes_admin_filter_by_proxy(
    test_db_session: Session, setup_test_data
):
    """测试管理员按代理商筛选可用卡密"""
    # 创建管理员用户
    admin_user = User(
        username="admin_test2", email="admin_test2@example.com", role=Role.ADMIN
    )
    admin_user.set_password("password123")
    test_db_session.add(admin_user)
    test_db_session.commit()
    test_db_session.refresh(admin_user)

    # 创建代理商用户
    proxy_user = User(
        username="proxy_test", email="proxy_test@example.com", role=Role.PROXY
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    # 创建测试卡密
    _, cards = setup_test_data
    card_id = cards[0].id
    _ = create_activation_codes(test_db_session, card_id, 2)  # 普通卡密
    _ = create_activation_codes(
        test_db_session, card_id, 3, proxy_user.id
    )  # 代理商卡密

    # 管理员获取所有可用卡密
    all_codes, all_count = get_available_activation_codes(test_db_session, admin_user)
    assert len(all_codes) == 5
    assert all_count == 5


def test_get_available_activation_codes_proxy_own(
    test_db_session: Session, setup_test_data
):
    """测试代理商获取自己名下的可用卡密"""
    # 创建代理商用户
    proxy_user = User(
        username="proxy_test3", email="proxy_test3@example.com", role=Role.PROXY
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    # 创建另一个代理商用户
    other_proxy = User(
        username="other_proxy", email="other_proxy@example.com", role=Role.PROXY
    )
    other_proxy.set_password("password123")
    test_db_session.add(other_proxy)
    test_db_session.commit()
    test_db_session.refresh(other_proxy)

    # 创建测试卡密
    _, cards = setup_test_data
    card_id = cards[0].id
    _ = create_activation_codes(
        test_db_session, card_id, 2, proxy_user.id
    )  # 代理商1的卡密
    _ = create_activation_codes(
        test_db_session, card_id, 3, other_proxy.id
    )  # 代理商2的卡密

    # 代理商1获取自己的卡密
    own_codes, own_count = get_available_activation_codes(test_db_session, proxy_user)
    assert len(own_codes) == 2== 2== 2
    assert own_count == 2
    for code in own_codes:
        assert code.proxy_user_id == proxy_user.id


def test_get_available_activation_codes_proxy_no_cards(
    test_db_session: Session, setup_test_data
):
    """测试代理商没有卡密的情况"""
    # 创建代理商用户
    proxy_user = User(
        username="proxy_test4", email="proxy_test4@example.com", role=Role.PROXY
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    # 代理商获取自己的卡密（应该为空）
    own_codes, own_count = get_available_activation_codes(test_db_session, proxy_user)
    assert len(own_codes) == 0
    assert own_count == 0


def test_get_available_activation_codes_unauthorized(
    test_db_session: Session, setup_test_data
):
    """测试无权限用户访问可用卡密接口"""
    # 创建普通用户
    normal_user = User(
        username="normal_test", email="normal_test@example.com", role=Role.USER
    )
    normal_user.set_password("password123")
    test_db_session.add(normal_user)
    test_db_session.commit()
    test_db_session.refresh(normal_user)

    # 创建 STAFF 用户
    staff_user = User(
        username="staff_test", email="staff_test@example.com", role=Role.STAFF
    )
    staff_user.set_password("password123")
    test_db_session.add(staff_user)
    test_db_session.commit()
    test_db_session.refresh(staff_user)

    # 测试普通用户访问
    with pytest.raises(HTTPException) as exc_info:
        get_available_activation_codes(test_db_session, normal_user)
    assert exc_info.value.status_code == 403
    assert "无权限" in exc_info.value.detail

    # 测试 STAFF 用户访问
    with pytest.raises(HTTPException) as exc_info:
        get_available_activation_codes(test_db_session, staff_user)
    assert exc_info.value.status_code == 403
    assert "无权限" in exc_info.value.detail


def test_get_available_activation_codes_include_consumed(
    test_db_session: Session, setup_test_data
):
    """测试获取可用卡密时不包含已消费的卡密"""
    # 创建代理商用户
    proxy_user = User(
        username="proxy_test5", email="proxy_test5@example.com", role=Role.PROXY
    )
    proxy_user.set_password("password123")
    test_db_session.add(proxy_user)
    test_db_session.commit()
    test_db_session.refresh(proxy_user)

    # 创建测试卡密
    _, cards = setup_test_data
    card_id = cards[0].id
    codes = create_activation_codes(test_db_session, card_id, 3, proxy_user.id)

    # 将一个卡密标记为已消费
    from src.server.activation_code.service import set_code_consuming, set_code_consumed

    set_code_consuming(test_db_session, codes[0].code)
    set_code_consumed(test_db_session, codes[0].code)

    # 获取可用卡密
    available_codes, total_count = get_available_activation_codes(
        test_db_session, proxy_user
    )

    # 应该只返回2个可用卡密
    assert len(available_codes) == 2
    assert total_count == 2
    for code in available_codes:
        assert code.status == CardCodeStatus.AVAILABLE
