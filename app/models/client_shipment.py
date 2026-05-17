from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from .base import Base
from value_objects import Weight


class ClientShipment(Base):
    __tablename__ = "client_shipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    transport_id: Mapped[int] = mapped_column(
        ForeignKey("transports.id"), nullable=False
    )
    weight_grams: Mapped[int] = mapped_column(Integer, nullable=False)
    destination: Mapped[str] = mapped_column(String(500), nullable=False)
    pickup_address: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Value Object via SQLAlchemy composite
    weight: Mapped[Weight] = composite(Weight, "weight_grams")

    client: Mapped["User"] = relationship(
        back_populates="client_shipments", foreign_keys=[client_id]
    )
    transport: Mapped["Transport"] = relationship(back_populates="client_shipments")
    orders: Mapped[list["Order"]] = relationship(back_populates="client_shipment")

    def __repr__(self) -> str:
        return f"ClientShipment(id={self.id}, client_id={self.client_id})"
