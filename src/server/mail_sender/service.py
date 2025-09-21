# -*- coding: utf-8 -*-
"""
邮件发送服务

文件功能：
- 封装 SMTP 邮件发送逻辑，并提供业务侧可直接调用的邮件发送接口。

公开接口：
- send_mail
- send_purchase_confirmation_email
- send_verification_code_email

内部方法：
- _build_mime_message
- _format_recipients

文件的公开接口的 Pydantic 模型：
- MailContent（定义于 `schemas.py`）
- MailSendResult（定义于 `schemas.py`）
- PurchaseMailPayload（定义于 `schemas.py`）
- VerificationCodeMailPayload（定义于 `schemas.py`）
"""

from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Iterable

from loguru import logger

from src.server.config import global_config
from .config import mail_sender_config
from .schemas import (
    MailAddress,
    MailContent,
    MailSendResult,
    NewOrderNotificationPayload,
    PurchaseMailPayload,
    VerificationCodeMailPayload,
)


def _build_mime_message(mail: MailContent) -> MIMEText:
    """构造 MIME 消息对象"""
    if not mail.recipients:
        raise ValueError("收件人列表不能为空")

    message = MIMEText(mail.body, mail.subtype, "utf-8")
    sender_name = mail_sender_config.sender_name or mail_sender_config.sender_email
    message["From"] = formataddr((sender_name, mail_sender_config.sender_email))
    message["To"] = _format_recipients(mail.recipients)
    message["Subject"] = mail.subject
    return message


def _format_recipients(recipients: Iterable[MailAddress]) -> str:
    """将收件人列表格式化为字符串"""
    formatted = []
    for recipient in recipients:
        display_name = recipient.name or recipient.email
        formatted.append(formataddr((display_name, recipient.email)))
    return ", ".join(formatted)


def send_mail(mail: MailContent) -> MailSendResult:
    """发送邮件并返回结果"""
    try:
        message = _build_mime_message(mail)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"邮件内容构造失败：{exc}")
        return MailSendResult(success=False, error=str(exc))

    smtp_class = smtplib.SMTP_SSL if mail_sender_config.use_ssl else smtplib.SMTP

    mail_sent = False

    try:
        with smtp_class(
            mail_sender_config.smtp_host,
            mail_sender_config.smtp_port,
            timeout=mail_sender_config.timeout,
        ) as server:
            if not mail_sender_config.use_ssl and mail_sender_config.use_tls:
                server.starttls()
            server.login(
                mail_sender_config.sender_email, mail_sender_config.sender_password
            )
            server.sendmail(
                mail_sender_config.sender_email,
                [recipient.email for recipient in mail.recipients],
                message.as_string(),
            )
            mail_sent = True
    except smtplib.SMTPServerDisconnected as exc:
        if mail_sent:
            logger.warning(f"邮件发送成功但服务器提前断开连接：{exc}")
            return MailSendResult(success=True, error=None)
        logger.error(f"邮件发送失败：{exc}")
        return MailSendResult(success=False, error=str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.error(f"邮件发送失败：{exc}")
        return MailSendResult(success=False, error=str(exc))

    logger.info("邮件发送成功")
    return MailSendResult(success=True, error=None)


def send_purchase_confirmation_email(
    payload: PurchaseMailPayload,
) -> MailSendResult:
    """发送购买成功提醒邮件"""
    purchased_at_display = payload.purchased_at.isoformat()
    body_lines = [
        f"您好，{payload.recipient.name or payload.recipient.email}",
        "",
        f"您已成功购买充值卡「{payload.card_name}」，下方附上卡密信息：",
        f"收件邮箱：{payload.recipient.email}",
        f"卡密：{payload.activation_code}",
        f"金额：{payload.sale_price:.2f} 元",
        f"购买时间：{purchased_at_display}",
        "",
        "请妥善保管卡密，若非本人操作请及时联系客服。",
        "",
        "感谢您的支持，祝您使用愉快！",
    ]
    mail = MailContent(
        subject=f"充值卡「{payload.card_name}」购买成功",
        body="\n".join(body_lines),
        recipients=[payload.recipient],
    )
    return send_mail(mail)


def send_verification_code_email(
    payload: VerificationCodeMailPayload,
) -> MailSendResult:
    """发送验证码邮件"""
    body_lines = [
        f"您好，{payload.recipient.name or payload.recipient.email}",
        "",
        f"您的验证码为：{payload.code}",
        f"验证码有效期：{payload.expires_in_minutes} 分钟，请勿泄露给他人。",
        "",
        "如果非本人操作，请尽快更改账号密码或联系管理员。",
    ]
    mail = MailContent(
        subject="账户安全验证码",
        body="\n".join(body_lines),
        recipients=[payload.recipient],
    )
    return send_mail(mail)


def send_new_order_notification_email(
    payload: NewOrderNotificationPayload,
) -> MailSendResult:
    """发送新订单通知邮件"""
    created_at_display = payload.created_at.isoformat()
    # 构造 HTML 正文
    body_html = f"""
    <p>您好，{payload.recipient.name or payload.recipient.email}</p>
    <p>您负责的渠道「{payload.channel_name}」有新的订单需要处理：</p>
    <ul>
      <li>订单ID：{payload.order_id}</li>
      <li>商品名称：{payload.card_name}</li>
      <li>卡密：{payload.activation_code}</li>
      <li>创建时间：{created_at_display}</li>
    </ul>
    <p>请及时
       <a href="{global_config.app_url}/staff/order-processing">登录系统</a>
       处理该订单。
    </p>
    <p>系统自动发送，请勿回复此邮件。</p>
    """
    mail = MailContent(
        subject=f"渠道「{payload.channel_name}」新订单通知",
        body=body_html,
        recipients=[payload.recipient],
        subtype="html",  # 👈 这里很重要：告诉发送函数这是 HTML 邮件
    )
    return send_mail(mail)

__all__ = [
    "send_mail",
    "send_new_order_notification_email",
    "send_purchase_confirmation_email",
    "send_verification_code_email",
]
