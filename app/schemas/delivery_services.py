from pydantic import BaseModel, Field, model_validator

from value_objects import Duration, Price


class PriceRead(BaseModel):
    kopecks: int
    rubles: float
    format: str
    model_config = {"from_attributes": True}


class DurationRead(BaseModel):
    seconds: int
    minutes: int
    model_config = {"from_attributes": True}


class DeliveryServiceRead(BaseModel):
    id: int
    name: str
    price: PriceRead
    time: DurationRead
    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_vos(cls, data: object) -> object:
        if hasattr(data, "price") and isinstance(data.price, Price):
            p = data.price
            data.__dict__["price"] = {
                "kopecks": p.kopecks,
                "rubles": p.rubles,
                "format": p.format,
            }
        if hasattr(data, "duration") and isinstance(data.duration, Duration):
            d = data.duration
            data.__dict__["time"] = {
                "seconds": d.seconds,
                "minutes": d.minutes,
            }
        return data


class DeliveryServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price_rubles: float = Field(..., gt=0, description="Цена в рублях")
    time_minutes: int = Field(..., gt=0, description="Время выполнения в минутах")


class DeliveryServiceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    price_rubles: float | None = Field(None, gt=0)
    time_minutes: int | None = Field(None, gt=0)
