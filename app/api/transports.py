from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from authentication import current_admin, current_active_user
from config import settings
from models import db_helper, Transport, TransportCategory, User
from schemas.transports import TransportCreate, TransportRead, TransportUpdate
from services.transports import TransportService

router = APIRouter(tags=["Transports"], prefix=settings.url.transports)


class TransportFilter(Filter):
    model__like: str | None = None
    category_id: int | None = None
    order_by: list[str] | None = ["id"]

    class Constants(Filter.Constants):
        model = Transport
        ordering_field_name = "order_by"


@router.get("", response_model=Page[TransportRead], description="**Сортировка (order_by):** id, model, category_id. Префикс `-` для DESC, например: `-id`")
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    transport_filter: TransportFilter = FilterDepends(TransportFilter),
    _: User = Depends(current_active_user),
):
    stmt = select(Transport).options(joinedload(Transport.category))
    stmt = transport_filter.filter(stmt)
    stmt = transport_filter.sort(stmt)
    return await apaginate(session, stmt)


@router.post("", response_model=TransportRead, status_code=status.HTTP_201_CREATED)
async def store(
    data: TransportCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = TransportService(session)
    transport = await svc.create(data)
    await session.commit()
    return await svc.get_by_id(transport.id)


@router.get("/{transport_id}", response_model=TransportRead)
async def show(
    transport_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_active_user),
):
    svc = TransportService(session)
    return await svc.get_by_id(transport_id)


@router.put("/{transport_id}", response_model=TransportRead)
async def update(
    transport_id: int,
    data: TransportUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = TransportService(session)
    transport = await svc.update(transport_id, data)
    await session.commit()
    return await svc.get_by_id(transport_id)


@router.delete("/{transport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    transport_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = TransportService(session)
    await svc.delete(transport_id)
    await session.commit()
