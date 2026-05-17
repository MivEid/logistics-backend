from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import Order, STATUS_IN_PROGRESS, STATUS_COMPLETED
from repositories.orders import OrderRepository
from repositories.delivery_services import DeliveryServiceRepository
from repositories.client_shipments import ClientShipmentRepository
from repositories.users import UserRepository
from schemas.orders import OrderCreate, OrderUpdate, OrderStatusUpdate, OrderAddServices
from services.email_service import EmailService


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = OrderRepository(session)
        self.service_repo = DeliveryServiceRepository(session)
        self.shipment_repo = ClientShipmentRepository(session)
        self.user_repo = UserRepository(session)
        self.email_svc = EmailService()

    async def get_for_user(self, user_id: int, role_id: int) -> list[Order]:
        if role_id == 1:
            return await self.repo.get_all()
        elif role_id == 2:
            return await self.repo.get_by_courier(user_id)
        else:
            return await self.repo.get_by_client(user_id)

    async def get_by_id_for_user(
        self, order_id: int, user_id: int, role_id: int
    ) -> Order:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ {order_id} не найден",
            )
        if role_id == 2 and order.courier_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете просматривать только свои заказы",
            )
        if role_id == 3 and order.client_shipment.client_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете просматривать только свои заказы",
            )
        return order

    async def create(self, data: OrderCreate, admin_id: int) -> Order:
        shipment = await self.shipment_repo.get_by_id(data.client_shipment_id)
        if not shipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Груз {data.client_shipment_id} не найден",
            )
        courier = await self.user_repo.get_by_id(data.courier_id)
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Курьер {data.courier_id} не найден",
            )
        if courier.role_id != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Выбранный пользователь не является курьером",
            )

        services = await self.service_repo.get_many_by_ids(data.service_ids)
        if len(services) != len(data.service_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Одна или несколько услуг не найдены",
            )

        total_seconds = sum(s.time_seconds for s in services)
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(seconds=total_seconds)

        order = await self.repo.create(
            {
                "administrator_id": admin_id,
                "courier_id": data.courier_id,
                "client_shipment_id": data.client_shipment_id,
                "status": STATUS_IN_PROGRESS,
                "start_date": start_date,
                "end_date": end_date,
                "version": 0,
            }
        )

        for service_id in data.service_ids:
            await self.repo.add_service(order.id, service_id)

        return await self.repo.get_by_id(order.id)

    async def update(self, order_id: int, data: OrderUpdate) -> Order:
        order = await self._get_editable_order(order_id)

        if order.version != data.version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Конфликт версий: заказ был изменён другим запросом (optimistic lock)",
            )

        update_data = data.model_dump(exclude_unset=True, exclude={"version"})

        if "courier_id" in update_data:
            courier = await self.user_repo.get_by_id(update_data["courier_id"])
            if not courier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Курьер {update_data['courier_id']} не найден",
                )
            if courier.role_id != 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Выбранный пользователь не является курьером",
                )

        if "client_shipment_id" in update_data:
            shipment = await self.shipment_repo.get_by_id(update_data["client_shipment_id"])
            if not shipment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Груз {update_data['client_shipment_id']} не найден",
                )

        update_data["version"] = order.version + 1
        return await self.repo.update(order, update_data)

    async def update_status(self, order_id: int, data: OrderStatusUpdate) -> Order:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ {order_id} не найден",
            )
        if not order.can_transition_to(data.status):
            from models.order import STATUS_LABELS
            current_label = STATUS_LABELS.get(order.status, str(order.status))
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Нельзя перевести заказ из статуса '{current_label}' в статус {data.status}",
            )

        order = await self.repo.update(order, {"status": data.status})

        if data.status == STATUS_COMPLETED:
            client = order.client_shipment.client
            if client and client.is_send_notify and client.email:
                await self.email_svc.send_order_completed(client.email, order_id)

        return order

    async def add_services(self, order_id: int, data: OrderAddServices) -> Order:
        order = await self._get_editable_order(order_id)

        existing_ids = await self.repo.get_service_ids(order_id)
        duplicates = [sid for sid in data.service_ids if sid in existing_ids]
        if duplicates:
            services = await self.service_repo.get_many_by_ids(duplicates)
            names = ", ".join(f"'{s.name}'" for s in services)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Следующие услуги уже добавлены в заказ: {names}",
            )

        new_services = await self.service_repo.get_many_by_ids(data.service_ids)
        if len(new_services) != len(data.service_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Одна или несколько услуг не найдены",
            )

        for service_id in data.service_ids:
            await self.repo.add_service(order_id, service_id)

        updated = await self.repo.get_by_id(order_id)
        total_seconds = updated.total_time_seconds
        end_date = updated.start_date + timedelta(seconds=total_seconds)
        return await self.repo.update(updated, {"end_date": end_date})

    async def delete(self, order_id: int) -> None:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ {order_id} не найден",
            )
        await self.repo.delete(order)

    async def _get_editable_order(self, order_id: int) -> Order:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ {order_id} не найден",
            )
        if order.is_completed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Нельзя редактировать завершённый заказ",
            )
        return order
