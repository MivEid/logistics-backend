from fastapi import APIRouter

from config import settings
from .auth import router as auth_router
from .users import router as users_router
from .transport_categories import router as transport_categories_router
from .transports import router as transports_router
from .delivery_services import router as delivery_services_router
from .client_shipments import router as client_shipments_router
from .orders import router as orders_router

router = APIRouter(prefix=settings.url.prefix)

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(transport_categories_router)
router.include_router(transports_router)
router.include_router(delivery_services_router)
router.include_router(client_shipments_router)
router.include_router(orders_router)
