from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TransportCategory(Base):
    __tablename__ = "transport_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    transports: Mapped[list["Transport"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"TransportCategory(id={self.id}, name={self.name})"
