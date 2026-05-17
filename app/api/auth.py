from fastapi import APIRouter

from authentication import auth_backend, fastapi_users
from schemas.users import UserRead, UserCreate
from config import settings

router = APIRouter(tags=["Auth"], prefix=settings.url.auth)

router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_reset_password_router())
