# -*- coding: utf-8 -*-

from sqlalchemy.orm import Session
from src.server.auth.models import User
from src.server.auth.schemas import Role


def create_user_helper(
    test_db_session: Session,
    username: str,
    email: str,
    password: str,
    role: Role = Role.USER,
) -> User:
    """辅助函数：直接在数据库中创建用户"""
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


def get_auth_token(test_client, username: str, password: str) -> str:
    """辅助函数：获取用户认证token"""
    login_resp = test_client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert login_resp.status_code == 200, f"登录失败: {login_resp.text}"
    return login_resp.json()["access_token"]


def test_admin_update_user_success(test_client, test_db_session):
    """测试管理员成功更新用户信息"""
    # 创建一个普通用户
    user = create_user_helper(
        test_db_session, "testuser", "test@example.com", "password123"
    )

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 更新用户信息
    update_data = {"name": "Updated Name", "status": "active"}

    resp = test_client.put(
        f"/api/auth/admin/users/{user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 200
    updated_user = resp.json()
    assert updated_user["name"] == "Updated Name"
    assert updated_user["status"] == "active"
    assert updated_user["id"] == user.id


def test_admin_update_user_not_found(test_client, test_db_session):
    """测试管理员更新不存在的用户"""
    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 尝试更新不存在的用户
    update_data = {"name": "Updated Name"}

    resp = test_client.put(
        "/api/auth/admin/users/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 400
    assert "不存在" in resp.json()["detail"]


def test_admin_update_user_email_conflict(test_client, test_db_session):
    """测试管理员更新用户邮箱时邮箱冲突"""
    # 创建两个用户
    user1 = create_user_helper(
        test_db_session, "user1", "user1@example.com", "password123"
    )
    _ = create_user_helper(test_db_session, "user2", "user2@example.com", "password123")

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 尝试将user1的邮箱更新为user2的邮箱
    update_data = {"email": "user2@example.com"}

    resp = test_client.put(
        f"/api/auth/admin/users/{user1.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 400
    assert "已被其他用户使用" in resp.json()["detail"]


def test_admin_update_user_unauthorized(test_client, test_db_session):
    """测试非管理员用户访问管理员更新路由"""
    # 创建一个普通用户
    user = create_user_helper(
        test_db_session, "user", "user@example.com", "password123"
    )

    # 获取普通用户token
    user_token = get_auth_token(test_client, "user", "password123")

    # 尝试更新用户信息
    update_data = {"name": "Updated Name"}

    resp = test_client.put(
        f"/api/auth/admin/users/{user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert resp.status_code == 403
    assert "无权限" in resp.json()["detail"]


def test_admin_update_user_invalid_channel(test_client, test_db_session):
    """测试管理员更新用户为STAFF角色但指定了不存在的渠道"""
    # 创建一个用户
    user = create_user_helper(
        test_db_session, "user", "user@example.com", "password123"
    )

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 尝试更新用户为STAFF角色但指定不存在的渠道
    update_data = {"role": "staff", "channel_id": 99999}

    resp = test_client.put(
        f"/api/auth/admin/users/{user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 400
    assert "渠道" in resp.json()["detail"]


def test_admin_get_user_success(test_client, test_db_session):
    """测试管理员成功获取指定用户信息"""
    # 创建一个普通用户
    user = create_user_helper(
        test_db_session, "testuser", "test@example.com", "password123"
    )

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 获取用户信息
    resp = test_client.get(
        f"/api/auth/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 200
    user_data = resp.json()
    assert user_data["id"] == user.id
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "test@example.com"


def test_admin_get_user_not_found(test_client, test_db_session):
    """测试管理员获取不存在的用户"""
    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 尝试获取不存在的用户
    resp = test_client.get(
        "/api/auth/admin/users/99999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 404
    assert "用户不存在" in resp.json()["detail"]


def test_admin_get_user_unauthorized(test_client, test_db_session):
    """测试非管理员用户访问管理员获取用户路由"""
    # 创建一个普通用户
    user = create_user_helper(
        test_db_session, "user", "user@example.com", "password123"
    )

    # 获取普通用户token
    user_token = get_auth_token(test_client, "user", "password123")

    # 尝试获取用户信息
    resp = test_client.get(
        f"/api/auth/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert resp.status_code == 403
    assert "无权限" in resp.json()["detail"]


def test_admin_delete_user_success(test_client, test_db_session):
    """测试管理员成功删除用户"""
    # 创建一个普通用户
    user = create_user_helper(
        test_db_session, "testuser", "test@example.com", "password123"
    )

    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 删除用户
    resp = test_client.delete(
        f"/api/auth/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 200
    assert "用户删除成功" in resp.json()["message"]

    # 验证用户已被删除
    from src.server.auth.dao import UserDAO

    deleted_user = UserDAO(test_db_session).get_by_id(user.id)
    assert deleted_user is None


def test_admin_delete_user_not_found(test_client, test_db_session):
    """测试管理员删除不存在的用户"""
    # 创建管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 尝试删除不存在的用户
    resp = test_client.delete(
        "/api/auth/admin/users/99999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 404
    assert "用户不存在" in resp.json()["detail"]


def test_admin_delete_user_admin_protection(test_client, test_db_session):
    """测试管理员不能删除其他管理员用户"""
    # 创建一个管理员用户
    admin_user = create_user_helper(
        test_db_session, "admin2", "admin2@example.com", "admin123", Role.ADMIN
    )

    # 创建另一个管理员用户
    _ = create_user_helper(
        test_db_session, "admin", "admin@example.com", "admin123", Role.ADMIN
    )

    # 获取管理员token
    admin_token = get_auth_token(test_client, "admin", "admin123")

    # 尝试删除另一个管理员用户
    resp = test_client.delete(
        f"/api/auth/admin/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 400
    assert "不能删除管理员用户" in resp.json()["detail"]


def test_admin_delete_user_unauthorized(test_client, test_db_session):
    """测试非管理员用户访问管理员删除用户路由"""
    # 创建一个普通用户
    user = create_user_helper(
        test_db_session, "user", "user@example.com", "password123"
    )

    # 获取普通用户token
    user_token = get_auth_token(test_client, "user", "password123")

    # 尝试删除用户
    resp = test_client.delete(
        f"/api/auth/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert resp.status_code == 403
    assert "无权限" in resp.json()["detail"]
