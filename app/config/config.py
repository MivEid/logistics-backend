from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта (папка logistics/), независимо от того, откуда запущен скрипт
_BASE_DIR = Path(__file__).resolve().parent.parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = False
    future: bool = True


class UrlPrefix(BaseModel):
    prefix: str = "/api"
    auth: str = "/auth"
    users: str = "/users"
    transport_categories: str = "/transport-categories"
    transports: str = "/transports"
    delivery_services: str = "/delivery-services"
    client_shipments: str = "/client-shipments"
    orders: str = "/orders"

    @property
    def bearer_token_url(self) -> str:
        parts = (self.prefix, self.auth, "/login")
        path = "".join(parts)
        return path.removeprefix("/")


class AccessTokenConfig(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class MailConfig(BaseModel):
    host: str = "localhost"
    port: int = 1025
    from_address: str = "noreply@logistics-system.com"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_BASE_DIR / ".env.template"), str(_BASE_DIR / ".env")),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    url: UrlPrefix = UrlPrefix()
    db: DatabaseConfig
    access_token: AccessTokenConfig
    mail: MailConfig = MailConfig()


settings = Settings()
