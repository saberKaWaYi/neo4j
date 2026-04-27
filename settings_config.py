from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

LogServiceName = Literal["crawler", "web", "worker"]


class Settings(BaseSettings):

    """全局配置"""
    debug: bool = False

    """nebula服务配置"""
    nebula_host: str = Field(default="127.0.0.1", alias="NEBULA_HOST")
    nebula_port: int = Field(default=9669, alias="NEBULA_PORT")
    nebula_username: str = Field(default="root", alias="NEBULA_USERNAME")
    nebula_password: str = Field(default="nebula", alias="NEBULA_PASSWORD")
    businesses: list[str] = Field(default_factory=lambda: ["genshin"], alias="BUSINESSES")

    """rabbitmq服务配置"""
    rabbitmq_host: str = Field(default="127.0.0.1", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, alias="RABBITMQ_PORT")
    rabbitmq_username: str = Field(default="guest", alias="RABBITMQ_USERNAME")
    rabbitmq_password: str = Field(default="guest", alias="RABBITMQ_PASSWORD")
    rabbitmq_queue_nebula: str = Field(default="nebula_operations", alias="RABBITMQ_QUEUE_NEBULA")
    rabbitmq_queue_mongo: str = Field(default="mongo_operations", alias="RABBITMQ_QUEUE_MONGO")

    """crawler服务配置"""
    crawler_debug: bool = Field(default=False, alias="CRAWLER_DEBUG")
    crawler_cookies: str = Field(...,alias="CRAWLER_COOKIES")
    crawler_headers: str = Field(..., alias="CRAWLER_HEADERS")
    crawler_time_sleep: int = Field(default=3, alias="CRAWLER_TIME_SLEEP")
    crawler_max_retries: int = Field(default=15, alias="CRAWLER_MAX_RETRIES")

    """web服务配置"""
    web_debug: bool = Field(default=False, alias="WEB_DEBUG")
    web_name: str = Field(default="Web Service", alias="WEB_NAME")
    web_version: str = Field(default="1.0", alias="WEB_VERSION")

    """worker服务配置"""
    worker_debug: bool = Field(default=False, alias="WORKER_DEBUG")

    @field_validator("businesses", mode="before")
    @classmethod
    def parse_businesses(cls, value):
        if isinstance(value, str):
            items = [item.strip() for item in value.split(",") if item.strip()]
            if not items:
                raise ValueError("BUSINESSES must include at least one business")
            return items
        raise ValueError("BUSINESSES must be a comma-separated string")

    def get_service_debug(self, service: LogServiceName) -> bool:
        service_debug_map = {
            "web": self.web_debug,
            "crawler": self.crawler_debug,
            "worker": self.worker_debug,
        }
        service_debug = service_debug_map[service]
        if service_debug is None:
            return self.debug
        return service_debug

settings = Settings()