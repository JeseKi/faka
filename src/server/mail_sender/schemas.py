# -*- coding: utf-8 -*-
"""
邮件发送模块数据模型

文件功能：
- 定义邮件发送模块使用的 Pydantic 数据模型。

公开接口：
- MailAddress
- MailContent
- MailSendResult
- PurchaseMailPayload
- VerificationCodeMailPayload

内部方法：
- 无

文件的公开接口的 Pydantic 模型：
- MailAddress
- MailContent
- MailSendResult
- PurchaseMailPayload
- VerificationCodeMailPayload
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class MailAddress(BaseModel):
    """邮件地址信息"""

    email: EmailStr = Field(..., description="邮箱地址")
    name: str | None = Field(default=None, description="收件人名称", max_length=100)


class MailContent(BaseModel):
    """邮件正文内容"""

    subject: str = Field(..., min_length=1, max_length=120, description="邮件主题")
    body: str = Field(..., min_length=1, description="邮件正文")
    recipients: list[MailAddress] = Field(..., min_length=1, description="收件人列表")
    subtype: Literal["plain", "html"] = Field(
        default="plain", description="邮件正文格式"
    )


class MailSendResult(BaseModel):
    """邮件发送结果"""

    success: bool = Field(..., description="是否发送成功")
    error: str | None = Field(default=None, description="错误信息")


class PurchaseMailPayload(BaseModel):
    """购买成功邮件上下文"""

    recipient: MailAddress = Field(..., description="收件人信息")
    card_name: str = Field(..., min_length=1, max_length=100, description="购买的卡名称")
    activation_code: str = Field(..., min_length=1, description="卡密")
    sale_price: float = Field(..., ge=0, description="销售价格")
    purchased_at: datetime = Field(..., description="购买时间")


class VerificationCodeMailPayload(BaseModel):
    """验证码邮件上下文"""

    recipient: MailAddress = Field(..., description="收件人信息")
    code: str = Field(..., min_length=4, max_length=12, description="验证码内容")
    expires_in_minutes: int = Field(..., ge=1, le=60, description="验证码有效分钟数")


__all__ = [
    "MailAddress",
    "MailContent",
    "MailSendResult",
    "PurchaseMailPayload",
    "VerificationCodeMailPayload",
]
