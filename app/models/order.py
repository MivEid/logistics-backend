from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

STATUS_IN_PROGRESS = 1
STATUS_COMPLETED = 2

VALID_TRANSITIONS = {
    STATUS_IN_PROGRESS: [STATUS_COMPLETED],
    STATUS_COMPLETED: [],
}

STATUS_LABELS = {
    STATUS_IN_PROGRESS: "в работе",
    STATUS_COMPLETED: "завершён",
}


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    administrator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    courier_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    client_shipment_id: Mapped[int] = mapped_column(
        ForeignKey("client_shipments.id"), nullable=False
    )
    status: Mapped[int] = mapped_column(Integer, default=STATUS_IN_PROGRESS, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    administrator: Mapped["User"] = relationship(
        back_populates="orders_as_admin", foreign_keys=[administrator_id]
    )
    courier: Mapped["User"] = relationship(
        back_populates="orders_as_courier", foreign_keys=[courier_id]
    )
    client_shipment: Mapped["ClientShipment"] = relationship(back_populates="orders")
    order_services: Mapped[list["OrderService"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def total_price_kopecks(self) -> int:
        return sum(os.service.price_kopecks for os in self.order_services)

    @property
    def total_price_rubles(self) -> float:
        return self.total_price_kopecks / 100

    @property
    def total_time_seconds(self) -> int:
        return sum(os.service.time_seconds for os in self.order_services)

    @property
    def total_time_minutes(self) -> int:
        return self.total_time_seconds // 60

    @property
    def is_completed(self) -> bool:
        return self.status == STATUS_COMPLETED

    def can_transition_to(self, new_status: int) -> bool:
        return new_status in VALID_TRANSITIONS.get(self.status, [])

    def __repr__(self) -> str:
        return f"Order(id={self.id}, status={self.status})"


class OrderService(Base):
    __tablename__ = "order_services"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_services.id"), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="order_services")
    service: Mapped["DeliveryService"] = relationship(back_populates="order_services")

    def __repr__(self) -> str:
        return f"OrderService(order_id={self.order_id}, service_id={self.service_id})"
