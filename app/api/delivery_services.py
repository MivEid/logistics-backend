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
from models import db_helper, DeliveryService, User
from schemas.delivery_services import (
    DeliveryServiceCreate,
    DeliveryServiceRead,
    DeliveryServiceUpdate,
)
from services.delivery_services import DeliveryServiceService

router = APIRouter(tags=["Delivery Services"], prefix=settings.url.delivery_services)


class DeliveryServiceFilter(Filter):
    name__like: str | None = None
    price_kopecks__lte: int | None = None
    price_kopecks__gte: int | None = None
    order_by: list[str] | None = ["id"]

    class Constants(Filter.Constants):
        model = DeliveryService
        ordering_field_name = "order_by"


@router.get("", response_model=Page[DeliveryServiceRead], description="**Сортировка (order_by):** id, name, price_kopecks, time_seconds. Префикс `-` для DESC, например: `-price_kopecks`")
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    service_filter: DeliveryServiceFilter = FilterDepends(DeliveryServiceFilter),
    _: User = Depends(current_active_user),
):
    stmt = select(DeliveryService)
    stmt = service_filter.filter(stmt)
    stmt = service_filter.sort(stmt)
    return await apaginate(session, stmt)


@router.post("", response_model=DeliveryServiceRead, status_code=status.HTTP_201_CREATED)
async def store(
    data: DeliveryServiceCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = DeliveryServiceService(session)
    service = await svc.create(data)
    await session.commit()
    await session.refresh(service)
    return service


@router.get("/{service_id}", response_model=DeliveryServiceRead)
async def show(
    service_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_active_user),
):
    svc = DeliveryServiceService(session)
    return await svc.get_by_id(service_id)


@router.put("/{service_id}", response_model=DeliveryServiceRead)
async def update(
    service_id: int,
    data: DeliveryServiceUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = DeliveryServiceService(session)
    service = await svc.update(service_id, data)
    await session.commit()
    await session.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    service_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = DeliveryServiceService(session)
    await svc.delete(service_id)
    await session.commit()
