from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models import Order, OrderService, ClientShipment, Transport


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _full_query(self):
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

    async def get_all(self) -> list[Order]:
        result = await self.session.scalars(self._full_query())
        return list(result.unique().all())

    async def get_by_courier(self, courier_id: int) -> list[Order]:
        result = await self.session.scalars(
            self._full_query().where(Order.courier_id == courier_id)
        )
        return list(result.unique().all())

    async def get_by_client(self, client_id: int) -> list[Order]:
        result = await self.session.scalars(
            self._full_query()
            .join(Order.client_shipment)
            .where(ClientShipment.client_id == client_id)
        )
        return list(result.unique().all())

    async def get_by_id(self, order_id: int) -> Order | None:
        return await self.session.scalar(
            self._full_query()
            .where(Order.id == order_id)
            .execution_options(populate_existing=True)
        )

    async def create(self, data: dict) -> Order:
        order = Order(**data)
        self.session.add(order)
        await self.session.flush()
        return order

    async def update(self, order: Order, data: dict) -> Order:
        for field, value in data.items():
            setattr(order, field, value)
        await self.session.flush()
        return await self.get_by_id(order.id)

    async def delete(self, order: Order) -> None:
        await self.session.delete(order)
        await self.session.flush()

    async def add_service(self, order_id: int, service_id: int) -> OrderService:
        os = OrderService(order_id=order_id, service_id=service_id)
        self.session.add(os)
        await self.session.flush()
        return os

    async def get_service_ids(self, order_id: int) -> list[int]:
        result = await self.session.scalars(
            select(OrderService.service_id).where(OrderService.order_id == order_id)
        )
        return list(result.all())
