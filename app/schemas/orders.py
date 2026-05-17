from datetime import datetime

from pydantic import BaseModel, Field

from .client_shipments import ClientShipmentRead
from .delivery_services import DeliveryServiceRead
from .users import UserShortRead


class OrderServiceRead(BaseModel):
    id: int
    service_id: int
    service: DeliveryServiceRead | None = None
    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: int
    status: int
    start_date: datetime
    end_date: datetime
    total_price_rubles: float
    total_time_minutes: int
    version: int
    administrator: UserShortRead | None = None
    courier: UserShortRead | None = None
    client_shipment: ClientShipmentRead | None = None
    order_services: list[OrderServiceRead] = []
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    courier_id: int
    client_shipment_id: int
    service_ids: list[int] = Field(..., min_length=1, description="Список id услуг")


class OrderUpdate(BaseModel):
    courier_id: int | None = None
    client_shipment_id: int | None = None
    version: int = Field(..., description="Текущая версия заказа (optimistic lock)")


class OrderStatusUpdate(BaseModel):
    status: int = Field(..., ge=1, le=2, description="1 = в работе, 2 = завершён")


class OrderAddServices(BaseModel):
    service_ids: list[int] = Field(..., min_length=1, description="ID услуг для добавления")
