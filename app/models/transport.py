from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Transport(Base):
    __tablename__ = "transports"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("transport_categories.id"), nullable=False
    )
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped["TransportCategory"] = relationship(back_populates="transports")
    client_shipments: Mapped[list["ClientShipment"]] = relationship(
        back_populates="transport"
    )

    def __repr__(self) -> str:
        return f"Transport(id={self.id}, model={self.model})"
