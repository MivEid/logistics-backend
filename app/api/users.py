from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from authentication import current_admin, current_active_user
from config import settings
from models import db_helper, User
from schemas.users import UserListRead, UserUpdate
from services.users import UserService

router = APIRouter(tags=["Users"], prefix=settings.url.users)


class UserFilter(Filter):
    role_id: int | None = None
    is_active: bool | None = None
    order_by: list[str] | None = ["-id"]

    class Constants(Filter.Constants):
        model = User
        ordering_field_name = "order_by"


@router.get("", response_model=Page[UserListRead])
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_filter: UserFilter = FilterDepends(UserFilter),
    _current_user: User = Depends(current_active_user),
):
    stmt = select(User).options(joinedload(User.role))
    stmt = user_filter.filter(stmt)
    stmt = user_filter.sort(stmt)
    return await apaginate(session, stmt)


@router.get("/me", response_model=UserListRead)
async def get_me(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: User = Depends(current_active_user),
):
    svc = UserService(session)
    return await svc.get_by_id(current_user.id)


@router.patch("/me", response_model=UserListRead)
async def update_me(
    data: UserUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: User = Depends(current_active_user),
):
    svc = UserService(session)
    return await svc.update(current_user.id, data.model_dump(exclude_unset=True), allow_role_change=False)


@router.get("/{user_id}", response_model=UserListRead)
async def show(
    user_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _current_user: User = Depends(current_active_user),
):
    svc = UserService(session)
    return await svc.get_by_id(user_id)


@router.patch("/{user_id}", response_model=UserListRead)
async def update_user(
    user_id: int,
    data: UserUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _current_user: User = Depends(current_admin),
):
    svc = UserService(session)
    return await svc.update(user_id, data.model_dump(exclude_unset=True), allow_role_change=True)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: User = Depends(current_admin),
):
    svc = UserService(session)
    await svc.delete(user_id, current_user.id)
