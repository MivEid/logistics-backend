from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authentication import current_admin, current_active_user
from config import settings
from models import db_helper, TransportCategory, User
from schemas.transport_categories import (
    TransportCategoryCreate,
    TransportCategoryRead,
    TransportCategoryUpdate,
)
from services.transport_categories import TransportCategoryService

router = APIRouter(
    tags=["Transport Categories"], prefix=settings.url.transport_categories
)


class TransportCategoryFilter(Filter):
    name__like: str | None = None
    order_by: list[str] | None = ["id"]

    class Constants(Filter.Constants):
        model = TransportCategory
        ordering_field_name = "order_by"


@router.get("", response_model=Page[TransportCategoryRead])
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    category_filter: TransportCategoryFilter = FilterDepends(TransportCategoryFilter),
    _: User = Depends(current_active_user),
):
    stmt = select(TransportCategory)
    stmt = category_filter.filter(stmt)
    stmt = category_filter.sort(stmt)
    return await apaginate(session, stmt)


@router.post("", response_model=TransportCategoryRead, status_code=status.HTTP_201_CREATED)
async def store(
    data: TransportCategoryCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = TransportCategoryService(session)
    category = await svc.create(data)
    await session.commit()
    return category


@router.get("/{category_id}", response_model=TransportCategoryRead)
async def show(
    category_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_active_user),
):
    svc = TransportCategoryService(session)
    return await svc.get_by_id(category_id)


@router.put("/{category_id}", response_model=TransportCategoryRead)
async def update(
    category_id: int,
    data: TransportCategoryUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = TransportCategoryService(session)
    category = await svc.update(category_id, data)
    await session.commit()
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    category_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = TransportCategoryService(session)
    await svc.delete(category_id)
    await session.commit()
