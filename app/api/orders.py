from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from authentication import current_admin, current_active_user
from config import settings
from models import db_helper, Order, OrderService, ClientShipment, Transport, User
from schemas.orders import (
    OrderAddServices,
    OrderCreate,
    OrderRead,
    OrderStatusUpdate,
    OrderUpdate,
)
from services.orders import OrderService as OrderServiceClass

router = APIRouter(tags=["Orders"], prefix=settings.url.orders)


class OrderFilter(Filter):
    status: int | None = None
    courier_id: int | None = None
    administrator_id: int | None = None
    order_by: list[str] | None = ["-id"]

    class Constants(Filter.Constants):
        model = Order
        ordering_field_name = "order_by"


def _full_order_query():
    return (
        select(Order)
        .options(
            joinedload(Order.administrator),
            joinedload(Order.courier),
            joinedload(Order.client_shipment)
            .joinedload(ClientShipment.client),
            joinedload(Order.client_shipment)
            .joinedload(ClientShipment.transport)
            .joinedload(Transport.category),
            selectinload(Order.order_services)
            .joinedload(OrderService.service),
        )
    )


@router.get("", response_model=Page[OrderRead], description="**Сортировка (order_by):** id, status, start_date, end_date, courier_id. Префикс `-` для DESC, например: `-start_date`")
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    order_filter: OrderFilter = FilterDepends(OrderFilter),
    current_user: User = Depends(current_active_user),
):
    stmt = _full_order_query()

    if current_user.role_id == 2:
        stmt = stmt.where(Order.courier_id == current_user.id)
    elif current_user.role_id == 3:
        stmt = stmt.join(Order.client_shipment).where(
            ClientShipment.client_id == current_user.id
        )

    stmt = order_filter.filter(stmt)
    stmt = order_filter.sort(stmt)
    return await apaginate(session, stmt)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def store(
    data: OrderCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: User = Depends(current_admin),
):
    svc = OrderServiceClass(session)
    order = await svc.create(data, current_user.id)
    await session.commit()
    return await svc.repo.get_by_id(order.id)


@router.get("/{order_id}", response_model=OrderRead)
async def show(
    order_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: User = Depends(current_active_user),
):
    svc = OrderServiceClass(session)
    return await svc.get_by_id_for_user(order_id, current_user.id, current_user.role_id)


@router.put("/{order_id}", response_model=OrderRead)
async def update(
    order_id: int,
    data: OrderUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = OrderServiceClass(session)
    order = await svc.update(order_id, data)
    await session.commit()
    return await svc.repo.get_by_id(order_id)


@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = OrderServiceClass(session)
    order = await svc.update_status(order_id, data)
    await session.commit()
    return await svc.repo.get_by_id(order_id)


@router.post(
    "/{order_id}/services",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_services(
    order_id: int,
    data: OrderAddServices,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = OrderServiceClass(session)
    order = await svc.add_services(order_id, data)
    await session.commit()
    return await svc.repo.get_by_id(order_id)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    order_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = OrderServiceClass(session)
    await svc.delete(order_id)
    await session.commit()
