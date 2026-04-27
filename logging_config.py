import logging
import logging.config

from pathlib import Path
from typing import Literal

from settings_config import settings

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

WEB_LOG = LOG_DIR / "web.log"
CRAWLER_LOG = LOG_DIR / "crawler.log"
WORKER_LOG = LOG_DIR / "worker.log"

LogService = Literal["web", "crawler", "worker"]


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


def _logging_dict_web(debug: bool) -> dict:
    level = "DEBUG" if debug else "INFO"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _standard_formatters(),
        "handlers": {
            "web_file": {
                "class": "logging.FileHandler",
                "filename": str(WEB_LOG),
                "formatter": "standard",
                "level": level,
                "encoding": "utf-8",
            },
            "console": _console_handler(),
        },
        "loggers": {
            "app": {
                "handlers": ["web_file", "console"],
                "level": level,
                "propagate": False,
            },
            "services": {
                "handlers": ["web_file", "console"],
                "level": level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["web_file", "console"],
                "level": level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["web_file", "console"],
                "level": level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["web_file", "console"],
                "level": level,
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["web_file", "console"],
                "level": level,
                "propagate": False,
            },
        },
    }


def _logging_dict_crawler(debug: bool) -> dict:
    level = "DEBUG" if debug else "INFO"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _standard_formatters(),
        "handlers": {
            "crawler_file": {
                "class": "logging.FileHandler",
                "filename": str(CRAWLER_LOG),
                "formatter": "standard",
                "level": level,
                "encoding": "utf-8",
            },
            "console": _console_handler(),
        },
        "loggers": {
            "crawler": {
                "handlers": ["crawler_file", "console"],
                "level": level,
                "propagate": False,
            },
            "services": {
                "handlers": ["crawler_file", "console"],
                "level": level,
                "propagate": False,
            },
        },
    }


def _logging_dict_worker(debug: bool) -> dict:
    level = "DEBUG" if debug else "INFO"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _standard_formatters(),
        "handlers": {
            "worker_file": {
                "class": "logging.FileHandler",
                "filename": str(WORKER_LOG),
                "formatter": "standard",
                "level": level,
                "encoding": "utf-8",
            },
            "console": _console_handler(),
        },
        "loggers": {
            "worker": {
                "handlers": ["worker_file", "console"],
                "level": level,
                "propagate": False,
            },
            "services": {
                "handlers": ["worker_file", "console"],
                "level": level,
                "propagate": False,
            },
        },
    }


def setup_logging(service: LogService, *, debug: bool | None = None) -> None:
    effective_debug = settings.get_service_debug(service) if debug is None else debug
    builders = {
        "web": _logging_dict_web,
        "crawler": _logging_dict_crawler,
        "worker": _logging_dict_worker,
    }
    builder = builders.get(service)
    if builder is None:
        raise ValueError(f"Unknown log service: {service!r}; expected one of {tuple(builders)}")
    logging.config.dictConfig(builder(effective_debug))