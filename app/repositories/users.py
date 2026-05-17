from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _with_role(self):
        return select(User).options(joinedload(User.role))

    async def get_all(self) -> list[User]:
        result = await self.session.scalars(self._with_role())
        return list(result.unique().all())

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.scalar(
            self._with_role().where(User.id == user_id)
        )

    async def get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(
            self._with_role().where(User.email == email)
        )
