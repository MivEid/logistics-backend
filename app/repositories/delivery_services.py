from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import DeliveryService


class DeliveryServiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[DeliveryService]:
        result = await self.session.scalars(select(DeliveryService))
        return list(result.all())

    async def get_by_id(self, service_id: int) -> DeliveryService | None:
        return await self.session.get(DeliveryService, service_id)

    async def get_by_name(self, name: str) -> DeliveryService | None:
        return await self.session.scalar(
            select(DeliveryService).where(DeliveryService.name == name)
        )

    async def get_many_by_ids(self, ids: list[int]) -> list[DeliveryService]:
        result = await self.session.scalars(
            select(DeliveryService).where(DeliveryService.id.in_(ids))
        )
        return list(result.all())

    async def create(self, data: dict) -> DeliveryService:
        service = DeliveryService(**data)
        self.session.add(service)
        await self.session.flush()
        await self.session.refresh(service)
        return service

    async def update(self, service: DeliveryService, data: dict) -> DeliveryService:
        for field, value in data.items():
            setattr(service, field, value)
        await self.session.flush()
        await self.session.refresh(service)
        return service

    async def delete(self, service: DeliveryService) -> None:
        await self.session.delete(service)
        await self.session.flush()
