from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from .base import Base
from value_objects import Duration, Price


class DeliveryService(Base):
    __tablename__ = "delivery_services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    price_kopecks: Mapped[int] = mapped_column(Integer, nullable=False)
    time_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    # Value Objects via SQLAlchemy composite
    price: Mapped[Price] = composite(Price, "price_kopecks")
    duration: Mapped[Duration] = composite(Duration, "time_seconds")

    order_services: Mapped[list["OrderService"]] = relationship(
        back_populates="service"
    )

    def __repr__(self) -> str:
        return f"DeliveryService(id={self.id}, name={self.name})"
