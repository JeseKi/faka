# -*- coding: utf-8 -*-
"""
FastAPI 应用入口（模板版）

公开接口：
- `app`: FastAPI 实例

内部方法：
- 无

说明：
- 启动时初始化数据库
- 仅挂载 `auth` 与 `example_module` 两个模块
"""

from contextlib import asynccontextmanager
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server.config import global_config
from src.server.database import init_database, get_database_info

# 路由模块
from src.server.auth.router import router as auth_router
from src.server.example_module.router import router as example_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """生命周期管理：启动时检查/初始化数据库。"""
    logger.info("正在启动模板应用...")
    db_info = get_database_info()
    if not db_info.database_exists:
        logger.info("数据库不存在，正在初始化...")
        init_database()
        logger.info("数据库初始化完成")
    else:
        logger.info(f"数据库已存在，大小: {db_info.database_size} 字节")

    logger.info("应用启动完成")
    yield


app = FastAPI(title="Backend Template (Auth + DB + Example)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=global_config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(auth_router)
app.include_router(example_router)
