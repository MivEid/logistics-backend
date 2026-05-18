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
from models import db_helper, ClientShipment, Transport, TransportCategory, User
from schemas.client_shipments import (
    ClientShipmentCreate,
    ClientShipmentRead,
    ClientShipmentUpdate,
)
from services.client_shipments import ClientShipmentService

router = APIRouter(tags=["Client Shipments"], prefix=settings.url.client_shipments)


class ClientShipmentFilter(Filter):
    client_id: int | None = None
    transport_id: int | None = None
    destination__like: str | None = None
    order_by: list[str] | None = ["-id"]

    class Constants(Filter.Constants):
        model = ClientShipment
        ordering_field_name = "order_by"


@router.get("", response_model=Page[ClientShipmentRead], description="**Сортировка (order_by):** id, client_id, transport_id, destination. Префикс `-` для DESC, например: `-id`")
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    shipment_filter: ClientShipmentFilter = FilterDepends(ClientShipmentFilter),
    current_user: User = Depends(current_active_user),
):
    stmt = (
        select(ClientShipment)
        .options(
            joinedload(ClientShipment.client),
            joinedload(ClientShipment.transport).joinedload(Transport.category),
        )
    )
    if current_user.role_id == 3:
        stmt = stmt.where(ClientShipment.client_id == current_user.id)

    stmt = shipment_filter.filter(stmt)
    stmt = shipment_filter.sort(stmt)
    return await apaginate(session, stmt)


@router.post("", response_model=ClientShipmentRead, status_code=status.HTTP_201_CREATED)
async def store(
    data: ClientShipmentCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: User = Depends(current_active_user),
):
    if current_user.role_id == 3:
        data = data.model_copy(update={"client_id": current_user.id})
    elif data.client_id is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Поле client_id обязательно для администратора")
    svc = ClientShipmentService(session)
    shipment = await svc.create(data)
    await session.commit()
    return await svc.get_by_id(shipment.id)


@router.get("/{shipment_id}", response_model=ClientShipmentRead)
async def show(
    shipment_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: User = Depends(current_active_user),
):
    svc = ClientShipmentService(session)
    shipment = await svc.get_by_id(shipment_id)
    if current_user.role_id == 3 and shipment.client_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return shipment


@router.put("/{shipment_id}", response_model=ClientShipmentRead)
async def update(
    shipment_id: int,
    data: ClientShipmentUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = ClientShipmentService(session)
    shipment = await svc.update(shipment_id, data)
    await session.commit()
    return await svc.get_by_id(shipment.id)


@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    shipment_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: User = Depends(current_admin),
):
    svc = ClientShipmentService(session)
    await svc.delete(shipment_id)
    await session.commit()
