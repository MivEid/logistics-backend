from pydantic import BaseModel, Field, model_validator

from value_objects import Weight
from .transports import TransportRead
from .users import UserShortRead


class WeightRead(BaseModel):
    grams: int
    kg: float
    format: str
    model_config = {"from_attributes": True}


class ClientShipmentRead(BaseModel):
    id: int
    client_id: int
    transport_id: int
    destination: str
    pickup_address: str
    description: str | None
    weight: WeightRead
    client: UserShortRead | None = None
    transport: TransportRead | None = None
    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_weight_vo(cls, data: object) -> object:
        if hasattr(data, "weight") and isinstance(data.weight, Weight):
            w = data.weight
            data.__dict__["weight"] = {
                "grams": w.grams,
                "kg": w.kg,
                "format": w.format,
            }
        return data


class ClientShipmentCreate(BaseModel):
    client_id: int
    transport_id: int
    weight_kg: float = Field(..., gt=0, description="Вес груза в килограммах")
    destination: str = Field(..., min_length=1, max_length=500)
    pickup_address: str = Field(..., min_length=1, max_length=500)
    description: str | None = None


class ClientShipmentUpdate(BaseModel):
    client_id: int | None = None
    transport_id: int | None = None
    weight_kg: float | None = Field(None, gt=0)
    destination: str | None = Field(None, min_length=1, max_length=500)
    pickup_address: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
