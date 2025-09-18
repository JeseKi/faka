# -*- coding: utf-8 -*-
"""
示例模块路由（模板版）

公开接口：
- GET /api/example/ping
- POST /api/example/items
- GET /api/example/items/{item_id}
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from .schemas import ItemCreate, ItemOut
from . import service
from src.server.dao.dao_base import run_in_thread

router = APIRouter(prefix="/api/example", tags=["example"])


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}


@router.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    def _create():
        return service.create_item(db, payload.name)

    return await run_in_thread(_create)


@router.get("/items/{item_id}", response_model=ItemOut)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    def _get():
        return service.get_item(db, item_id)

    return await run_in_thread(_get)
