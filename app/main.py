from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.rabbitmq_service import RabbitMQService
from app.api.v1.router import api_router

from config import setup_logging, settings

setup_logging("web")

rabbitmq_service: RabbitMQService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global rabbitmq_service

    rabbitmq_service = RabbitMQService(
        host=settings.rabbitmq.host,
        port=settings.rabbitmq.port,
        username=settings.rabbitmq.username,
        password=settings.rabbitmq.password,
        queue_names=[
            settings.rabbitmq.queue_nebula,
            settings.rabbitmq.queue_mongo,
        ],
    )
    rabbitmq_service.connect()

    yield

    rabbitmq_service.disconnect()


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.app.app_name,
        version=settings.app.app_version,
        debug=settings.app.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.app.api_prefix)

    return app


app = create_app()