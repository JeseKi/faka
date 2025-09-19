# -*- coding: utf-8 -*-
"""
邮件发送服务测试

文件功能：
- 覆盖邮件发送模块公开接口的成功与失败路径，确保边界条件行为符合预期。

公开接口：
- 无

内部方法：
- DummySMTP（测试桩，用于模拟 SMTP 服务器）

文件的公开接口的 Pydantic 模型：
- 无
"""

from __future__ import annotations

import smtplib
from datetime import datetime
from email import message_from_string
from email.header import decode_header
from smtplib import SMTPServerDisconnected
from types import SimpleNamespace

import pytest

from src.server.mail_sender import (
    MailAddress,
    MailContent,
    MailSendResult,
    PurchaseMailPayload,
    VerificationCodeMailPayload,
    send_mail,
    send_purchase_confirmation_email,
    send_verification_code_email,
)
from src.server.mail_sender import service as mail_service
from src.server.mail_sender.config import mail_sender_config


class DummySMTP:
    """用于模拟 SMTP 行为"""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.logged_in = None
        self.sent_messages = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        return None

    def login(self, email, password):
        self.logged_in = (email, password)

    def sendmail(self, sender, recipients, message):
        self.sent_messages.append((sender, recipients, message))


@pytest.fixture(autouse=True)
def setup_mail_config(monkeypatch):
    """统一设置邮件配置，避免读取真实环境变量"""
    monkeypatch.setattr(mail_sender_config, "smtp_host", "smtp.test", raising=False)
    monkeypatch.setattr(mail_sender_config, "smtp_port", 465, raising=False)
    monkeypatch.setattr(mail_sender_config, "timeout", 5, raising=False)
    monkeypatch.setattr(mail_sender_config, "sender_email", "sender@example.com", raising=False)
    monkeypatch.setattr(mail_sender_config, "sender_password", "secret", raising=False)
    monkeypatch.setattr(mail_sender_config, "sender_name", "测试发件人", raising=False)
    monkeypatch.setattr(mail_sender_config, "use_ssl", True, raising=False)
    monkeypatch.setattr(mail_sender_config, "use_tls", False, raising=False)
    yield


def test_send_mail_success(monkeypatch):
    """成功发送邮件"""
    dummy_instance = DummySMTP()
    monkeypatch.setattr(smtplib, "SMTP_SSL", lambda *args, **kwargs: dummy_instance)

    mail = MailContent(
        subject="测试邮件",
        body="这是一封测试邮件",
        recipients=[MailAddress(email="user@example.com", name="测试用户")],
    )

    result = send_mail(mail)

    assert isinstance(result, MailSendResult)
    assert result.success is True
    assert dummy_instance.logged_in == (
        mail_sender_config.sender_email,
        mail_sender_config.sender_password,
    )
    assert len(dummy_instance.sent_messages) == 1
    sender, recipients, message = dummy_instance.sent_messages[0]
    assert sender == mail_sender_config.sender_email
    assert recipients == ["user@example.com"]
    parsed = message_from_string(message)
    subject_header = decode_header(parsed["Subject"])[0]
    subject_value = (
        subject_header[0].decode(subject_header[1] or "utf-8")
        if isinstance(subject_header[0], bytes)
        else subject_header[0]
    )
    assert subject_value == mail.subject
    payload = parsed.get_payload(decode=True).decode("utf-8") # type: ignore
    assert mail.body in payload


def test_send_mail_server_disconnect_after_success(monkeypatch):
    """服务器发送后立刻断开时仍视为成功"""

    class DisconnectingSMTP(DummySMTP):
        def __exit__(self, exc_type, exc, tb):
            raise SMTPServerDisconnected("connection dropped")

    dummy_instance = DisconnectingSMTP()
    monkeypatch.setattr(smtplib, "SMTP_SSL", lambda *args, **kwargs: dummy_instance)

    mail = MailContent(
        subject="测试邮件",
        body="这是一封测试邮件",
        recipients=[MailAddress(email="user@example.com")],
    )

    result = send_mail(mail)

    assert isinstance(result, MailSendResult)
    assert result.success is True


def test_send_mail_failure(monkeypatch):
    """发送失败返回错误信息"""

    def _raise_exception(*args, **kwargs):
        raise smtplib.SMTPException("无法连接 SMTP")

    monkeypatch.setattr(smtplib, "SMTP_SSL", _raise_exception)

    mail = MailContent(
        subject="测试邮件",
        body="这是一封测试邮件",
        recipients=[MailAddress(email="user@example.com")],
    )

    result = send_mail(mail)

    assert result.success is False
    assert result.error is not None
    assert "无法连接" in result.error


def test_send_purchase_confirmation_email(monkeypatch):
    """购买成功邮件包装逻辑"""
    captured = SimpleNamespace(content=None)

    def _fake_send(mail_content):
        captured.content = mail_content
        return MailSendResult(success=True, error=None)

    monkeypatch.setattr(mail_service, "send_mail", _fake_send)

    payload = PurchaseMailPayload(
        recipient=MailAddress(email="buyer@example.com", name="买家"),
        card_name="高级充值卡",
        activation_code="ABC123",
        sale_price=99.9,
        purchased_at=datetime.now(),
    )

    result = send_purchase_confirmation_email(payload)

    assert result.success is True
    assert captured.content is not None
    assert payload.card_name in captured.content.subject
    assert payload.activation_code in captured.content.body
    assert payload.recipient.email in captured.content.body


def test_send_verification_code_email(monkeypatch):
    """验证码邮件包装逻辑"""
    captured = SimpleNamespace(content=None)

    def _fake_send(mail_content):
        captured.content = mail_content
        return MailSendResult(success=True, error=None)

    monkeypatch.setattr(mail_service, "send_mail", _fake_send)

    payload = VerificationCodeMailPayload(
        recipient=MailAddress(email="user@example.com", name="测试"),
        code="123456",
        expires_in_minutes=5,
    )

    result = send_verification_code_email(payload)

    assert result.success is True
    assert captured.content is not None
    assert payload.code in captured.content.body
    assert str(payload.expires_in_minutes) in captured.content.body
