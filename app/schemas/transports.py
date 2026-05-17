from pydantic import BaseModel, Field

from .transport_categories import TransportCategoryRead


class TransportRead(BaseModel):
    id: int
    model: str
    description: str | None
    category_id: int
    category: TransportCategoryRead | None = None
    model_config = {"from_attributes": True}


class TransportCreate(BaseModel):
    category_id: int
    model: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class TransportUpdate(BaseModel):
    category_id: int | None = None
    model: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
