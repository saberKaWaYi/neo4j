import logging
import logging.config

from pathlib import Path

from typing import Literal

from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

WEB_LOG = LOG_DIR / "web.log"
CRAWLER_LOG = LOG_DIR / "crawler.log"

LogService = Literal["web", "crawler"]


def _standard_formatters() -> dict:
    return {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    }


def _console_handler() -> dict:
    return {
        "class": "logging.StreamHandler",
        "formatter": "standard",
        "level": "DEBUG",
    }


def _logging_dict_web() -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _standard_formatters(),
        "handlers": {
            "web_file": {
                "class": "logging.FileHandler",
                "filename": str(WEB_LOG),
                "formatter": "standard",
                "level": "INFO",
                "encoding": "utf-8",
            },
            "console": _console_handler(),
        },
        "loggers": {
            "app": {
                "handlers": ["web_file", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["web_file", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["web_file", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["web_file", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["web_file", "console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


def _logging_dict_crawler() -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _standard_formatters(),
        "handlers": {
            "crawler_file": {
                "class": "logging.FileHandler",
                "filename": str(CRAWLER_LOG),
                "formatter": "standard",
                "level": "DEBUG",
                "encoding": "utf-8",
            },
            "console": _console_handler(),
        },
        "loggers": {
            "crawler": {
                "handlers": ["crawler_file", "console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }


def setup_logging(service: LogService) -> None:
    builders = {
        "web": _logging_dict_web,
        "crawler": _logging_dict_crawler,
    }
    builder = builders.get(service)
    if builder is None:
        raise ValueError(f"Unknown log service: {service!r}; expected one of {tuple(builders)}")
    logging.config.dictConfig(builder())


class CrawlerSettings:
    """爬虫配置"""
    website_cookies = {
        "wiki_biligame_com": {
            "cookie_name": {
                "SESSDATA": "80e2be21%2C1789203900%2C949ca%2A32CjD2Gvwg3haOu5McOA0u_hAKlykzCa6TzdsDlON4b_h26Jc82hpLsMRb8d9OHJ6phFASVmRBOXFxcFd1QUVZUTRuVXY1LU0tSjUyTnhfZEpSdWlFeVhlVUJNZkJOVVVYT2xiV3BZZFl6czFEM2dua3BELWhYWUt5SzBSNll2OGdZS0wwemRYV1lRIIEC"
            }
        }
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    }
    time_sleep = 3
    max_retries = 15


crawler_settings = CrawlerSettings()


class Settings(BaseSettings):
    """应用配置"""
    app_name: str = "Neo4j Operations API"
    app_version: str = "1.0"
    debug: bool = False

    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: str = Field(default="neo4j", alias="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", alias="NEO4J_DATABASE")

    rabbitmq_host: str = Field(default="localhost", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, alias="RABBITMQ_PORT")
    rabbitmq_username: str = Field(default="guest", alias="RABBITMQ_USERNAME")
    rabbitmq_password: str = Field(default="guest", alias="RABBITMQ_PASSWORD")
    rabbitmq_queue: str = Field(default="neo4j", alias="RABBITMQ_QUEUE")

    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()