from fastapi import APIRouter
from app.api.v1.endpoints import producer

router = APIRouter()

router.include_router(producer.router, prefix="/messages", tags=["messages"])