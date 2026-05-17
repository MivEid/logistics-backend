from fastapi import Depends, HTTPException, status
from fastapi_users import FastAPIUsers

from models import User
from .backend import auth_backend
from .helper.user_manager import get_user_manager

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)


async def current_admin(user: User = Depends(current_active_user)) -> User:
    if user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только администраторам",
        )
    return user


async def current_admin_or_courier(user: User = Depends(current_active_user)) -> User:
    if user.role_id not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только администраторам и курьерам",
        )
    return user
