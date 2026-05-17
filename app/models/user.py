from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False, default=3
    )
    is_send_notify: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped["Role"] = relationship(back_populates="users")
    client_shipments: Mapped[list["ClientShipment"]] = relationship(
        back_populates="client", foreign_keys="ClientShipment.client_id"
    )
    orders_as_admin: Mapped[list["Order"]] = relationship(
        back_populates="administrator", foreign_keys="Order.administrator_id"
    )
    orders_as_courier: Mapped[list["Order"]] = relationship(
        back_populates="courier", foreign_keys="Order.courier_id"
    )

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(p for p in parts if p)

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email})"
