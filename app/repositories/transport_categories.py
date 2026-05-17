from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import TransportCategory


class TransportCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[TransportCategory]:
        result = await self.session.scalars(select(TransportCategory))
        return list(result.all())

    async def get_by_id(self, category_id: int) -> TransportCategory | None:
        return await self.session.get(TransportCategory, category_id)

    async def get_by_name(self, name: str) -> TransportCategory | None:
        result = await self.session.scalar(
            select(TransportCategory).where(TransportCategory.name == name)
        )
        return result

    async def create(self, name: str) -> TransportCategory:
        category = TransportCategory(name=name)
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def update(self, category: TransportCategory, data: dict) -> TransportCategory:
        for field, value in data.items():
            setattr(category, field, value)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category: TransportCategory) -> None:
        await self.session.delete(category)
        await self.session.flush()
