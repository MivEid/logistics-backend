from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import DeliveryService
from repositories.delivery_services import DeliveryServiceRepository
from schemas.delivery_services import DeliveryServiceCreate, DeliveryServiceUpdate
from value_objects import Duration, Price


class DeliveryServiceService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = DeliveryServiceRepository(session)

    async def get_all(self) -> list[DeliveryService]:
        return await self.repo.get_all()

    async def get_by_id(self, service_id: int) -> DeliveryService:
        service = await self.repo.get_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Услуга доставки {service_id} не найдена",
            )
        return service

    async def create(self, data: DeliveryServiceCreate) -> DeliveryService:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Услуга с названием '{data.name}' уже существует",
            )
        price = Price.from_rubles(data.price_rubles)
        duration = Duration.from_minutes(data.time_minutes)
        return await self.repo.create(
            {
                "name": data.name,
                "price_kopecks": price.kopecks,
                "time_seconds": duration.seconds,
            }
        )

    async def update(self, service_id: int, data: DeliveryServiceUpdate) -> DeliveryService:
        service = await self.get_by_id(service_id)
        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data:
            existing = await self.repo.get_by_name(update_data["name"])
            if existing and existing.id != service_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Услуга с названием '{update_data['name']}' уже существует",
                )

        db_data: dict = {}
        if "name" in update_data:
            db_data["name"] = update_data["name"]
        if "price_rubles" in update_data:
            db_data["price_kopecks"] = Price.from_rubles(update_data["price_rubles"]).kopecks
        if "time_minutes" in update_data:
            db_data["time_seconds"] = Duration.from_minutes(update_data["time_minutes"]).seconds

        return await self.repo.update(service, db_data)

    async def delete(self, service_id: int) -> None:
        service = await self.get_by_id(service_id)
        await self.repo.delete(service)
