from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
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

ALLOWED_INCLUDE = {"courier", "administrator", "client_shipment", "services"}
ALLOWED_FIELDS = {"id", "status", "start_date", "end_date", "total_price_rubles", "total_time_minutes", "version"}


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


def _serialize_order(order: Order, include_set: set, fields_set: set) -> dict:
    data: dict = {
        "id": order.id,
        "status": order.status,
        "start_date": order.start_date.isoformat() if order.start_date else None,
        "end_date": order.end_date.isoformat() if order.end_date else None,
        "total_price_rubles": order.total_price_rubles,
        "total_time_minutes": order.total_time_minutes,
        "version": order.version,
    }

    if "courier" in include_set and order.courier:
        c = order.courier
        data["courier"] = {"id": c.id, "full_name": c.full_name, "email": c.email}

    if "administrator" in include_set and order.administrator:
        a = order.administrator
        data["administrator"] = {"id": a.id, "full_name": a.full_name, "email": a.email}

    if "client_shipment" in include_set:
        s = order.client_shipment
        data["client_shipment"] = {
            "id": s.id,
            "destination": s.destination,
            "pickup_address": s.pickup_address,
            "weight": s.weight.format,
            "client": {"id": s.client.id, "full_name": s.client.full_name} if s.client else None,
            "transport": {"id": s.transport.id, "model": s.transport.model} if s.transport else None,
        } if s else None

    if "services" in include_set:
        data["services"] = [
            {
                "id": os.service.id,
                "name": os.service.name,
                "price": os.service.price.format,
                "duration_minutes": os.service.duration.minutes,
            }
            for os in order.order_services if os.service
        ]

    if fields_set:
        relation_keys = include_set & {"courier", "administrator", "client_shipment", "services"}
        data = {k: v for k, v in data.items() if k in fields_set or k in relation_keys}

    return data


@router.get(
    "",
    description=(
        "**Сортировка (order_by):** id, status, start_date, end_date, courier_id. Префикс `-` для DESC.\n\n"
        "**include** — через запятую: `courier`, `administrator`, `client_shipment`, `services`\n\n"
        "**select** — через запятую: `id`, `status`, `start_date`, `end_date`, `total_price_rubles`, `total_time_minutes`, `version`"
    ),
)
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    order_filter: OrderFilter = FilterDepends(OrderFilter),
    current_user: User = Depends(current_active_user),
    include: str | None = Query(None, description="courier, administrator, client_shipment, services"),
    select_fields: str | None = Query(None, alias="select", description="id, status, start_date, end_date, total_price_rubles, total_time_minutes, version"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=200, description="Page size"),
):
    include_set = {i.strip() for i in include.split(",")} & ALLOWED_INCLUDE if include else set()
    fields_set = {f.strip() for f in select_fields.split(",")} & ALLOWED_FIELDS if select_fields else set()

    if not include_set and not fields_set:
        stmt = _full_order_query()
        if current_user.role_id == 2:
            stmt = stmt.where(Order.courier_id == current_user.id)
        elif current_user.role_id == 3:
            stmt = stmt.join(Order.client_shipment).where(ClientShipment.client_id == current_user.id)
        stmt = order_filter.filter(stmt)
        stmt = order_filter.sort(stmt)

        # fetch results and use the regular `paginate` helper to avoid
        # pagination context issues with `apaginate`
        result = await session.scalars(stmt)
        orders = list(result.unique().all())
        items = [OrderRead.model_validate(o) for o in orders]

        # manual pagination to avoid dependency on fastapi_pagination runtime config
        total = len(items)
        start = (page - 1) * size
        end = start + size
        paged = items[start:end]
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": paged,
        }

    stmt = _full_order_query()
    if current_user.role_id == 2:
        stmt = stmt.where(Order.courier_id == current_user.id)
    elif current_user.role_id == 3:
        stmt = stmt.join(Order.client_shipment).where(ClientShipment.client_id == current_user.id)
    stmt = order_filter.filter(stmt)
    stmt = order_filter.sort(stmt)

    result = await session.scalars(stmt)
    orders = list(result.unique().all())
    serialized = [_serialize_order(o, include_set, fields_set) for o in orders]

    total = len(serialized)
    start = (page - 1) * size
    end = start + size
    paged = serialized[start:end]
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": paged,
    }


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


@router.get(
    "/{order_id}",
    description=(
        "**include** — через запятую: `courier`, `administrator`, `client_shipment`, `services`\n\n"
        "**select** — через запятую: `id`, `status`, `start_date`, `end_date`, `total_price_rubles`, `total_time_minutes`, `version`"
    ),
)
async def show(
    order_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: User = Depends(current_active_user),
    include: str | None = Query(None, description="courier, administrator, client_shipment, services"),
    select_fields: str | None = Query(None, alias="select", description="id, status, start_date, end_date, total_price_rubles, total_time_minutes, version"),
):
    svc = OrderServiceClass(session)
    order = await svc.get_by_id_for_user(order_id, current_user.id, current_user.role_id)

    include_set = {i.strip() for i in include.split(",")} & ALLOWED_INCLUDE if include else set()
    fields_set = {f.strip() for f in select_fields.split(",")} & ALLOWED_FIELDS if select_fields else set()

    if not include_set and not fields_set:
        return OrderRead.model_validate(order)

    return _serialize_order(order, include_set, fields_set)


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
