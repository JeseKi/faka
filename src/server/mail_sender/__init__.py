# -*- coding: utf-8 -*-
"""
邮件发送模块入口

文件功能：
- 聚合邮件发送模块的公开接口，便于其他模块统一导入。

公开接口：
- MailAddress
- MailContent
- MailSendResult
- PurchaseMailPayload
- VerificationCodeMailPayload
- send_mail
- send_purchase_confirmation_email
- send_verification_code_email

内部方法：
- 无

文件的公开接口的 Pydantic 模型：
- MailAddress（定义于 `schemas.py`）
- MailContent（定义于 `schemas.py`）
- MailSendResult（定义于 `schemas.py`）
- PurchaseMailPayload（定义于 `schemas.py`）
- VerificationCodeMailPayload（定义于 `schemas.py`）
"""

from .schemas import (  # noqa: F401
    MailAddress,
    MailContent,
    MailSendResult,
    PurchaseMailPayload,
    VerificationCodeMailPayload,
)
from .service import (  # noqa: F401
    send_mail,
    send_purchase_confirmation_email,
    send_verification_code_email,
)

__all__ = [
    "MailAddress",
    "MailContent",
    "MailSendResult",
    "PurchaseMailPayload",
    "VerificationCodeMailPayload",
    "send_mail",
    "send_purchase_confirmation_email",
    "send_verification_code_email",
]
