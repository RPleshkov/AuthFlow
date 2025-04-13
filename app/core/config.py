from typing import Annotated

from pydantic import AnyUrl, BaseModel, BeforeValidator, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.utils import parse_cors


class PostgresConfig(BaseModel):

    server: str
    port: int
    user: str
    password: str
    db: str

    pool_size: int = 50
    max_overflow: int = 10
    echo: bool = False

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def get_uri(self):
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.server,
            port=self.port,
            path=self.db,
        )


class RedisConfig(BaseModel):

    host: str
    port: int
    db: str
    max_connections: int = 100
    decode_responses: bool = True

    @property
    def get_uri(self):
        return MultiHostUrl.build(
            scheme="redis",
            host=self.host,
            port=self.port,
            path=self.db,
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_prefix="ENV_",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )

    api_v1_str: str = "/api/v1"
    project_name: str = "AuthFlow"

    frontend_host: str
    backend_cors_origins: Annotated[
        list[AnyUrl] | str,
        BeforeValidator(parse_cors),
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.backend_cors_origins] + [
            self.frontend_host
        ]

    postgres: PostgresConfig
    redis: RedisConfig


settings = Settings()  # type: ignore
print(settings.redis.get_uri)
