from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from repositories.users import UserRepository

# Поля, которые разрешено обновлять напрямую (без спецобработки)
_ALLOWED_FIELDS = {"first_name", "last_name", "patronymic", "role_id", "is_send_notify", "is_active"}


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

    async def update(self, user_id: int, raw_data: dict, allow_role_change: bool = False) -> User:
        user = await self.get_by_id(user_id)
        allowed = _ALLOWED_FIELDS if allow_role_change else _ALLOWED_FIELDS - {"role_id"}
        update_data = {k: v for k, v in raw_data.items() if k in allowed and v is not None}
        return await self.repo.update(user, update_data)

    async def delete(self, user_id: int, current_user_id: int) -> None:
        if user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить собственный аккаунт",
            )
        user = await self.get_by_id(user_id)
        await self.repo.delete(user)
