from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from models import ClientShipment, Transport


class ClientShipmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _with_relations(self):
        return select(ClientShipment).options(
            joinedload(ClientShipment.client),
            joinedload(ClientShipment.transport).joinedload(Transport.category),
        )

    async def get_all(self) -> list[ClientShipment]:
        result = await self.session.scalars(self._with_relations())
        return list(result.unique().all())

    async def get_by_id(self, shipment_id: int) -> ClientShipment | None:
        return await self.session.scalar(
            self._with_relations().where(ClientShipment.id == shipment_id)
        )

    async def get_by_client(self, client_id: int) -> list[ClientShipment]:
        result = await self.session.scalars(
            self._with_relations().where(ClientShipment.client_id == client_id)
        )
        return list(result.unique().all())

    async def create(self, data: dict) -> ClientShipment:
        shipment = ClientShipment(**data)
        self.session.add(shipment)
        await self.session.flush()
        return await self.get_by_id(shipment.id)

    async def update(self, shipment: ClientShipment, data: dict) -> ClientShipment:
        for field, value in data.items():
            setattr(shipment, field, value)
        await self.session.flush()
        return await self.get_by_id(shipment.id)

    async def delete(self, shipment: ClientShipment) -> None:
        await self.session.delete(shipment)
        await self.session.flush()
