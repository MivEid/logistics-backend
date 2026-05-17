from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import Transport
from repositories.transports import TransportRepository
from repositories.transport_categories import TransportCategoryRepository
from schemas.transports import TransportCreate, TransportUpdate


class TransportService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TransportRepository(session)
        self.category_repo = TransportCategoryRepository(session)

    async def get_all(self) -> list[Transport]:
        return await self.repo.get_all()

    async def get_by_id(self, transport_id: int) -> Transport:
        transport = await self.repo.get_by_id(transport_id)
        if not transport:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Транспорт {transport_id} не найден",
            )
        return transport

    async def create(self, data: TransportCreate) -> Transport:
        category = await self.category_repo.get_by_id(data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория транспорта {data.category_id} не найдена",
            )
        return await self.repo.create(data.model_dump())

    async def update(self, transport_id: int, data: TransportUpdate) -> Transport:
        transport = await self.get_by_id(transport_id)
        update_data = data.model_dump(exclude_unset=True)
        if "category_id" in update_data:
            category = await self.category_repo.get_by_id(update_data["category_id"])
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Категория транспорта {update_data['category_id']} не найдена",
                )
        return await self.repo.update(transport, update_data)

    async def delete(self, transport_id: int) -> None:
        transport = await self.get_by_id(transport_id)
        await self.repo.delete(transport)
