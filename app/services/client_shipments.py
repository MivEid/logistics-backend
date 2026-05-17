from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import ClientShipment
from repositories.client_shipments import ClientShipmentRepository
from repositories.transports import TransportRepository
from repositories.users import UserRepository
from schemas.client_shipments import ClientShipmentCreate, ClientShipmentUpdate
from value_objects import Weight


class ClientShipmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ClientShipmentRepository(session)
        self.transport_repo = TransportRepository(session)
        self.user_repo = UserRepository(session)

    async def get_all(self) -> list[ClientShipment]:
        return await self.repo.get_all()

    async def get_by_id(self, shipment_id: int) -> ClientShipment:
        shipment = await self.repo.get_by_id(shipment_id)
        if not shipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Груз {shipment_id} не найден",
            )
        return shipment

    async def get_by_client(self, client_id: int) -> list[ClientShipment]:
        return await self.repo.get_by_client(client_id)

    async def create(self, data: ClientShipmentCreate) -> ClientShipment:
        client = await self.user_repo.get_by_id(data.client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Клиент {data.client_id} не найден",
            )
        if client.role_id != 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Выбранный пользователь не является клиентом",
            )
        transport = await self.transport_repo.get_by_id(data.transport_id)
        if not transport:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Транспорт {data.transport_id} не найден",
            )
        weight = Weight.from_kg(data.weight_kg)
        return await self.repo.create(
            {
                "client_id": data.client_id,
                "transport_id": data.transport_id,
                "weight_grams": weight.grams,
                "destination": data.destination,
                "pickup_address": data.pickup_address,
                "description": data.description,
            }
        )

    async def update(
        self, shipment_id: int, data: ClientShipmentUpdate
    ) -> ClientShipment:
        shipment = await self.get_by_id(shipment_id)
        update_data = data.model_dump(exclude_unset=True)

        db_data: dict = {}
        for field in ("client_id", "transport_id", "destination", "pickup_address", "description"):
            if field in update_data:
                db_data[field] = update_data[field]
        if "weight_kg" in update_data:
            db_data["weight_grams"] = Weight.from_kg(update_data["weight_kg"]).grams

        return await self.repo.update(shipment, db_data)

    async def delete(self, shipment_id: int) -> None:
        shipment = await self.get_by_id(shipment_id)
        await self.repo.delete(shipment)
