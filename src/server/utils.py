"""获取当前用户、管理员、工作人员

Raises:
    credentials_exception: 凭证异常
    credentials_exception: 凭证异常
    HTTPException: 无权限异常
    HTTPException: 无权限异常

Returns:
    User: 当前用户
    User: 当前管理员
    User: 当前工作人员
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session


from src.server.database import get_db
from src.server.config import global_config
from src.server.auth.config import auth_config
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.auth import service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if (
        global_config.app_env.lower() in ["dev", "test"]
        and token == auth_config.test_token
    ):
        user = db.query(User).filter(User.id == 1).first()
        if user:
            return user
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, auth_config.jwt_secret_key, algorithms=[auth_config.jwt_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = service.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """获取当前管理员"""
    user = await get_current_user(token, db)
    if user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    return user


async def get_current_staff(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """获取当前工作人员"""
    user = await get_current_user(token, db)
    if user.role != Role.STAFF and user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    return user
