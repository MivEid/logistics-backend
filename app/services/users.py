from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from repositories.users import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def get_all(self) -> list[User]:
        return await self.repo.get_all()

    async def get_by_id(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь {user_id} не найден",
            )
        return user
