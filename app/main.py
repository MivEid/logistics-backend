import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from api import router as api_router
from config import settings
from models import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()


main_app = FastAPI(
    title="Logistics & Delivery Management System",
    description="REST API для системы управления логистикой и доставкой",
    version="1.0.0",
    lifespan=lifespan,
)

main_app.include_router(api_router)

add_pagination(main_app)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
