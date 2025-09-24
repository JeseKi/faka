# -*- coding: utf-8 -*-
"""
认证模块路由聚合

公开接口：
- POST /api/auth/login - 用户登录
- POST /api/auth/refresh - 刷新访问令牌
- POST /api/auth/send-verification-code - 发送邮箱验证码
- POST /api/auth/register-with-code - 使用验证码注册用户
- GET /api/auth/profile - 获取用户个人资料
- PUT /api/auth/profile - 更新用户个人资料
- PUT /api/auth/password - 修改用户密码
- POST /api/auth/admin/users - 管理员创建用户
- PUT /api/auth/admin/users/{user_id} - 管理员更新指定用户
- GET /api/auth/admin/users - 管理员获取用户列表
- GET /api/auth/admin/users/{user_id} - 管理员获取指定用户
- DELETE /api/auth/admin/users/{user_id} - 管理员删除指定用户
"""

from __future__ import annotations

from fastapi import APIRouter

from .auth import router as auth_router
from .profile import router as profile_router
from .admin import router as admin_router

# 创建主路由器
router = APIRouter()

# 包含所有子路由
router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(admin_router)
