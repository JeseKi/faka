# -*- coding: utf-8 -*-
"""
认证与用户服务（模板版）

公开接口：
- get_user_by_username / get_user_by_id
- authenticate_user
- create_access_token / create_refresh_token
- create_user / update_user / change_password / admin_update_user
- get_users_by_role
- bootstrap_default_admin
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
import string
from typing import Optional, cast

from jose import jwt
from loguru import logger
from sqlalchemy.orm import Session

from .config import auth_config
from .models import User
from .schemas import Role, UserCreate, UserUpdate, AdminUserCreate, AdminUserUpdate
from .dao import UserDAO
from src.server.mail_sender import (
    MailAddress,
    VerificationCodeMailPayload,
    send_verification_code_email,
)
from src.server.config import global_config


# 用于存储验证码的字典，实际项目中建议使用Redis等缓存
verification_codes: dict[str, dict[str, str | datetime]] = {}


def generate_verification_code(length: int = 6) -> str:
    """生成指定长度的数字验证码"""
    return "".join(random.choices(string.digits, k=length))


def send_verification_code(email: str) -> str:
    """生成并发送验证码邮件"""
    code = generate_verification_code()
    expires_minutes = 5
    expiry = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    verification_codes[email] = {"code": code, "expiry": expiry}

    mail_result = send_verification_code_email(
        VerificationCodeMailPayload(
            recipient=MailAddress(email=email),
            code=code,
            expires_in_minutes=expires_minutes,
        )
    )

    if not mail_result.success:
        logger.error(f"验证码邮件发送失败：{mail_result.error}")
        if global_config.app_env not in {"dev", "test"}:
            verification_codes.pop(email, None)
            raise RuntimeError("验证码邮件发送失败")
        logger.warning("开发/测试环境忽略邮件发送失败，验证码仍可使用")

    logger.info(f"验证码已发送到 {email}")
    return code


def verify_code(email: str, code: str) -> bool:
    """验证邮箱和验证码是否匹配且未过期"""
    if email not in verification_codes:
        return False

    stored_data = verification_codes[email]
    stored_code = stored_data["code"]
    expiry = cast(datetime, stored_data["expiry"])

    # 检查验证码是否正确且未过期
    if stored_code == code and datetime.now(timezone.utc) < expiry:
        # 验证成功后删除验证码
        del verification_codes[email]
        return True

    return False


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return UserDAO(db).get_by_username(username)


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据用户ID获取用户信息"""
    return UserDAO(db).get_by_id(user_id)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not user.check_password(password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=auth_config.access_token_ttl_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, auth_config.jwt_secret_key, algorithm=auth_config.jwt_algorithm
    )


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=auth_config.refresh_token_ttl_days)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, auth_config.jwt_secret_key, algorithm=auth_config.jwt_algorithm
    )


def create_user(db: Session, user_data: UserCreate) -> User:
    # 先构造密码哈希
    tmp_user = User(username=user_data.username, email=user_data.email)
    tmp_user.set_password(user_data.password)
    return UserDAO(db).create(
        tmp_user.username, tmp_user.email, tmp_user.password_hash, tmp_user.role
    )


def admin_create_user(db: Session, user_data: AdminUserCreate) -> User:
    """管理员创建用户"""
    # 先构造密码哈希
    tmp_user = User(
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        channel_id=user_data.channel_id if user_data.role == Role.STAFF else None,
    )
    tmp_user.set_password(user_data.password)
    return UserDAO(db).create(
        tmp_user.username,
        tmp_user.email,
        tmp_user.password_hash,
        tmp_user.role,
        tmp_user.channel_id,
    )


def admin_update_user(db: Session, user_id: int, user_data: AdminUserUpdate) -> User:
    """管理员更新指定ID的用户信息"""
    user_dao = UserDAO(db)
    user = user_dao.get_by_id(user_id)

    if not user:
        raise ValueError(f"用户ID {user_id} 不存在")

    # 过滤掉None值，只更新提供的非空字段
    update_data = user_data.model_dump(exclude_unset=True)
    # 进一步过滤掉None值
    update_data = {k: v for k, v in update_data.items() if v is not None}

    # 如果更新邮箱，需要检查邮箱是否已被其他用户使用
    if "email" in update_data:
        existing_user = (
            db.query(User).filter(User.email == update_data["email"]).first()
        )
        if existing_user and existing_user.id != user_id:
            raise ValueError(f"邮箱 {update_data['email']} 已被其他用户使用")

    # 如果更新角色为STAFF且提供了channel_id，需要验证渠道是否存在
    if update_data.get("role") == Role.STAFF and "channel_id" in update_data:
        from src.server.channel.models import Channel

        channel = (
            db.query(Channel).filter(Channel.id == update_data["channel_id"]).first()
        )
        if not channel:
            raise ValueError(f"指定的渠道ID {update_data['channel_id']} 不存在")

    return user_dao.update(user, **update_data)


def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    update_data = user_data.model_dump(exclude_unset=True)
    return UserDAO(db).update(user, **update_data)


def change_password(
    db: Session, user: User, old_password: str, new_password: str
) -> bool:
    if not user.check_password(old_password):
        return False
    user.set_password(new_password)
    db.commit()
    return True


def get_users_by_role(
    db: Session, role: Optional[Role] = None, page: int = 1, page_size: int = 50
) -> tuple[list[User], int]:
    """根据角色获取用户列表，支持分页"""
    user_dao = UserDAO(db)

    if role:
        # 按角色筛选
        users = user_dao.get_by_role(role, page=page, page_size=page_size)
        total_count = user_dao.count_by_role(role)
    else:
        # 获取所有用户
        users = user_dao.get_all(page=page, page_size=page_size)
        total_count = user_dao.count_all()

    return users, total_count


def bootstrap_default_admin(session: Session) -> None:
    """引导默认管理员（幂等）。用户名取邮箱 @ 前缀。"""
    admin_email = auth_config.admin_email
    admin_username = "admin"
    user = get_user_by_username(session, admin_username)
    password = auth_config.admin_password
    if user:
        return
    try:
        admin_user_data = UserCreate(
            username=admin_username, email=admin_email, password=password
        )
        new_user = create_user(session, admin_user_data)
        new_user.role = Role.ADMIN
        session.commit()
        logger.info(f"已引导管理员用户：{admin_username}")
    except Exception as e:
        session.rollback()
        logger.warning(f"引导管理员异常（已忽略）：{e}")
