from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from models import Transport


class TransportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _with_category(self):
        return select(Transport).options(joinedload(Transport.category))

    async def get_all(self) -> list[Transport]:
        result = await self.session.scalars(self._with_category())
        return list(result.unique().all())

    async def get_by_id(self, transport_id: int) -> Transport | None:
        result = await self.session.scalar(
            self._with_category().where(Transport.id == transport_id)
        )
        return result

    async def create(self, data: dict) -> Transport:
        transport = Transport(**data)
        self.session.add(transport)
        await self.session.flush()
        result = await self.session.scalar(
            self._with_category().where(Transport.id == transport.id)
        )
        return result

    async def update(self, transport: Transport, data: dict) -> Transport:
        for field, value in data.items():
            setattr(transport, field, value)
        await self.session.flush()
        result = await self.session.scalar(
            self._with_category().where(Transport.id == transport.id)
        )
        return result

    async def delete(self, transport: Transport) -> None:
        await self.session.delete(transport)
        await self.session.flush()
