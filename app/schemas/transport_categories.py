from pydantic import BaseModel, Field


class TransportCategoryRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class TransportCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class TransportCategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
