from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings.common import common_settings
from settings.web import web_settings
from logging_config import setup_logging

setup_logging("web")

from services.rabbitmq_service import RabbitMQService

rabbitmq_service: RabbitMQService = None

from app.api.v1 import rabbitmq_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global rabbitmq_service

    rabbitmq_service = RabbitMQService(
        host=common_settings.rabbitmq_host,
        port=common_settings.rabbitmq_port,
        username=common_settings.rabbitmq_username,
        password=common_settings.rabbitmq_password,
        queue_names=[common_settings.rabbitmq_queue_nebula, common_settings.rabbitmq_queue_mongo],
    )
    rabbitmq_service.connect()

    yield

    rabbitmq_service.disconnect()


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=web_settings.web_name,
        version=web_settings.web_version,
        debug=web_settings.web_debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()
app.include_router(rabbitmq_message.router, prefix="/api/v1")
