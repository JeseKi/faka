#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化/检查模板数据库的 CLI

用法：
- python -m scripts.initdb --check   # 检查表
- python -m scripts.initdb --reset   # 重置并初始化
- python -m scripts.initdb           # 仅初始化（若不存在）
"""

from __future__ import annotations

import argparse
from pathlib import Path
from loguru import logger

from src.server.database import init_database, get_database_info, engine, SessionLocal
from src.server.auth.models import User
from src.server.auth.schemas import Role
from src.server.channel.models import Channel
from src.server.card.models import Card
from src.server.activation_code.models import ActivationCode


def seed_initial_data() -> None:
    """
    植入初始开发数据：渠道、员工、卡、卡密。

    公开接口：
    - 无公开接口（内部函数）

    内部方法：
    - 创建渠道、用户、卡、卡密数据
    """
    db = SessionLocal()
    try:
        logger.info("开始植入初始数据...")

        # 1. 检查并创建渠道
        channel_a = db.query(Channel).filter(Channel.name == "渠道 A").first()
        if not channel_a:
            channel_a = Channel(name="渠道 A", description="渠道 A 的描述")
            db.add(channel_a)
            logger.info("创建渠道：渠道 A")

        channel_b = db.query(Channel).filter(Channel.name == "渠道 B").first()
        if not channel_b:
            channel_b = Channel(name="渠道 B", description="渠道 B 的描述")
            db.add(channel_b)
            logger.info("创建渠道：渠道 B")

        # 提交渠道创建事务
        db.commit()

        # 2. 检查并创建员工用户
        staff_1 = db.query(User).filter(User.username == "staff-1").first()
        if not staff_1:
            staff_1 = User(
                username="staff-1",
                email="staff1@example.com",
                name="员工 1",
                role=Role.STAFF,
                channel_id=channel_a.id,
            )
            staff_1.set_password("staff123")
            db.add(staff_1)
            logger.info("创建员工用户：staff-1")

        staff_2 = db.query(User).filter(User.username == "staff-2").first()
        if not staff_2:
            staff_2 = User(
                username="staff-2",
                email="staff2@example.com",
                name="员工 2",
                role=Role.STAFF,
                channel_id=channel_b.id,
            )
            staff_2.set_password("staff123")
            db.add(staff_2)
            logger.info("创建员工用户：staff-2")

        # 2.5. 检查并创建代理商用户
        proxy_1 = db.query(User).filter(User.username == "proxy-1").first()
        if not proxy_1:
            proxy_1 = User(
                username="proxy-1",
                email="proxy1@example.com",
                name="代理商 1",
                role=Role.PROXY,
                channel_id=channel_a.id,
            )
            proxy_1.set_password("proxy123")
            db.add(proxy_1)
            logger.info("创建代理商用户：proxy-1")

        proxy_2 = db.query(User).filter(User.username == "proxy-2").first()
        if not proxy_2:
            proxy_2 = User(
                username="proxy-2",
                email="proxy2@example.com",
                name="代理商 2",
                role=Role.PROXY,
                channel_id=channel_b.id,
            )
            proxy_2.set_password("proxy123")
            db.add(proxy_2)
            logger.info("创建代理商用户：proxy-2")

        # 3. 检查并创建卡
        card_a = db.query(Card).filter(Card.name == "卡 A").first()
        if not card_a:
            card_a = Card(
                name="卡 A",
                description="卡 A 的描述",
                price=10.0,
                channel_id=channel_a.id,
            )
            db.add(card_a)
            logger.info("创建卡：卡 A")

        card_b = db.query(Card).filter(Card.name == "卡 B").first()
        if not card_b:
            card_b = Card(
                name="卡 B",
                description="卡 B 的描述",
                price=20.0,
                channel_id=channel_b.id,
            )
            db.add(card_b)
            logger.info("创建卡：卡 B")

        # 提交所有数据
        db.commit()

        # 4. 检查并创建卡密
        from src.server.crypto.service import generate_activation_code

        # 确保 card_a 和 card_b 已经刷新，以获取它们的 ID
        db.refresh(card_a)
        db.refresh(card_b)

        existing_codes_a = (
            db.query(ActivationCode).filter(ActivationCode.card_id == card_a.id).count()
        )
        if existing_codes_a < 10:
            for i in range(10 - existing_codes_a):
                # 生成激活码
                activation_code_value = generate_activation_code()

                activation_code = ActivationCode(
                    card_id=card_a.id,
                    code=activation_code_value,
                    proxy_user_id=proxy_1.id,
                )
                db.add(activation_code)
            logger.info("为卡 A 创建了 {} 个卡密", 10 - existing_codes_a)

        existing_codes_b = (
            db.query(ActivationCode).filter(ActivationCode.card_id == card_b.id).count()
        )
        if existing_codes_b < 10:
            for i in range(10 - existing_codes_b):
                # 生成激活码
                activation_code_value = generate_activation_code()

                activation_code = ActivationCode(
                    card_id=card_b.id,
                    code=activation_code_value,
                    proxy_user_id=proxy_2.id,
                )
                db.add(activation_code)
            logger.info("为卡 B 创建了 {} 个卡密", 10 - existing_codes_b)

        # 提交卡密数据
        db.commit()

        # 5. 检查并创建代理商与卡的关联
        from src.server.proxy.service import link_proxy_to_cards

        # 确保 proxy_1 和 proxy_2 已经刷新，以获取它们的 ID
        db.refresh(proxy_1)
        db.refresh(proxy_2)

        # 为代理商 1 绑定卡 A
        try:
            link_proxy_to_cards(db, proxy_1.id, [card_a.id])
            logger.info("代理商 proxy-1 已绑定卡 A")
        except Exception as e:
            logger.warning("代理商 proxy-1 绑定卡 A 时出现问题：{}", e)

        # 为代理商 2 绑定卡 B
        try:
            link_proxy_to_cards(db, proxy_2.id, [card_b.id])
            logger.info("代理商 proxy-2 已绑定卡 B")
        except Exception as e:
            logger.warning("代理商 proxy-2 绑定卡 B 时出现问题：{}", e)

        # 提交所有数据
        db.commit()
        logger.info("初始数据植入完成")

    except Exception as e:
        db.rollback()
        logger.error("植入初始数据时发生错误：{}", e)
        raise
    finally:
        db.close()


def reset_database() -> None:
    """删除数据库文件并重新初始化。仅用于开发。"""
    info = get_database_info()
    db_path = Path(info.database_path)
    try:
        engine.dispose()
    except Exception:
        pass
    if db_path.exists():
        db_path.unlink()
        logger.info("已删除数据库文件：{}", db_path)
    init_database()
    # 在初始化数据库后植入初始数据
    seed_initial_data()


def check_status() -> None:
    from sqlalchemy import inspect

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info("当前数据库表: {}", tables)


def main() -> None:
    parser = argparse.ArgumentParser(description="模板数据库工具")
    parser.add_argument(
        "--reset", action="store_true", help="重置数据库（删除后再初始化）"
    )
    parser.add_argument("--check", action="store_true", help="检查数据库状态")
    args = parser.parse_args()

    if args.check:
        check_status()
        return
    if args.reset:
        reset_database()
        return

    # 默认：仅初始化（幂等）
    init_database()


if __name__ == "__main__":
    main()
