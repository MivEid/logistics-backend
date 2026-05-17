from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import TransportCategory
from repositories.transport_categories import TransportCategoryRepository
from schemas.transport_categories import TransportCategoryCreate, TransportCategoryUpdate


class TransportCategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TransportCategoryRepository(session)

    async def get_all(self) -> list[TransportCategory]:
        return await self.repo.get_all()

    async def get_by_id(self, category_id: int) -> TransportCategory:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория транспорта {category_id} не найдена",
            )
        return category

    async def create(self, data: TransportCategoryCreate) -> TransportCategory:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Категория с названием '{data.name}' уже существует",
            )
        return await self.repo.create(data.name)

    async def update(
        self, category_id: int, data: TransportCategoryUpdate
    ) -> TransportCategory:
        category = await self.get_by_id(category_id)
        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data:
            existing = await self.repo.get_by_name(update_data["name"])
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Категория с названием '{update_data['name']}' уже существует",
                )
        return await self.repo.update(category, update_data)

    async def delete(self, category_id: int) -> None:
        category = await self.get_by_id(category_id)
        await self.repo.delete(category)
