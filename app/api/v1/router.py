from fastapi import APIRouter
from app.api.v1.endpoints import producer

api_router = APIRouter()

api_router.include_router(producer.router, prefix="/messages", tags=["messages"])