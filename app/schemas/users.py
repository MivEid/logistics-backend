from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, Field


class RoleRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    patronymic: str | None
    role_id: int
    is_send_notify: bool

    model_config = {"from_attributes": True}


class UserCreate(schemas.BaseUserCreate):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    patronymic: str | None = Field(None, max_length=100)
    role_id: int = Field(3, ge=1, le=3)
    is_send_notify: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    patronymic: str | None = Field(None, max_length=100)
    role_id: int | None = Field(None, ge=1, le=3)
    is_send_notify: bool | None = None


class UserShortRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    model_config = {"from_attributes": True}


class UserListRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    patronymic: str | None
    email: EmailStr
    role_id: int
    is_send_notify: bool
    is_active: bool
    role: RoleRead | None = None
    model_config = {"from_attributes": True}
