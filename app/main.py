from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router

from settings_config import settings
from logging_config import setup_logging

setup_logging("web")

from services.rabbitmq_service import RabbitMQService

rabbitmq_service: RabbitMQService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global rabbitmq_service

    rabbitmq_service = RabbitMQService(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        username=settings.rabbitmq_username,
        password=settings.rabbitmq_password,
        queue_names=[settings.rabbitmq_queue_nebula, settings.rabbitmq_queue_mongo],
    )
    rabbitmq_service.connect()

    yield

    rabbitmq_service.disconnect()


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.web_name,
        version=settings.web_version,
        debug=settings.web_debug,
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
app.include_router(api_router, prefix="/api/v1")