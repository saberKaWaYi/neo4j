from typing import Literal

from pydantic import Field, field_validator

from settings.base import EnvSettings

LogServiceName = Literal["crawler", "web", "worker"]


class CommonSettings(EnvSettings):
    debug: bool = Field(default=False, alias="DEBUG")

    nebula_host: str = Field(default="127.0.0.1", alias="NEBULA_HOST")
    nebula_port: int = Field(default=9669, alias="NEBULA_PORT")
    nebula_username: str = Field(default="root", alias="NEBULA_USERNAME")
    nebula_password: str = Field(default="nebula", alias="NEBULA_PASSWORD")
    businesses: list[str] = Field(default="genshin", alias="BUSINESSES")

    rabbitmq_host: str = Field(default="127.0.0.1", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, alias="RABBITMQ_PORT")
    rabbitmq_username: str = Field(default="guest", alias="RABBITMQ_USERNAME")
    rabbitmq_password: str = Field(default="guest", alias="RABBITMQ_PASSWORD")
    rabbitmq_queue_nebula: str = Field(default="nebula_operations", alias="RABBITMQ_QUEUE_NEBULA")
    rabbitmq_queue_mongo: str = Field(default="mongo_operations", alias="RABBITMQ_QUEUE_MONGO")

    @field_validator("businesses", mode="before")
    @classmethod
    def parse_businesses(cls, value):
        items = [item.strip() for item in value.split(",") if item.strip()]
        if not items:
            raise ValueError("BUSINESSES must include at least one business")
        return items


common_settings = CommonSettings()
