# -*- coding: utf-8 -*-
"""
邮件发送配置

文件功能：
- 提供邮件发送所需的环境配置项。

公开接口：
- mail_sender_config

内部方法：
- 无

文件的公开接口的 Pydantic 模型：
- MailSenderConfig
"""

from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class MailSenderConfig(BaseSettings):
    """邮件发送配置"""

    smtp_host: str = Field(default="smtp.qq.com", alias="MAIL_SMTP_HOST")
    smtp_port: int = Field(default=465, alias="MAIL_SMTP_PORT")
    use_ssl: bool = Field(default=True, alias="MAIL_USE_SSL")
    use_tls: bool = Field(default=False, alias="MAIL_USE_TLS")
    timeout: int = Field(default=5, alias="MAIL_TIMEOUT", description="SMTP 超时时间")
    sender_email: EmailStr = Field(default="", alias="SENDER_EMAIL")
    sender_password: str = Field(default="", alias="SENDER_PASSWORD")
    sender_name: str = Field(default="", alias="SENDER_NAME")


mail_sender_config = MailSenderConfig()

__all__ = ["mail_sender_config", "MailSenderConfig"]
