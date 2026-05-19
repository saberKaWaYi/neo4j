from fastapi import APIRouter, HTTPException
router = APIRouter()

import logging
logger = logging.getLogger(__name__)

from settings import common_settings

from services.rabbitmq_service import RabbitMQService
from models.schemas_message import NebulaOperationMessage, MessageResponse

from typing import Union
from datetime import datetime

def get_rabbitmq_service() -> RabbitMQService:
    from app.main import rabbitmq_service
    if not rabbitmq_service:
        raise HTTPException(status_code=503, detail="RabbitMQ service not available")
    return rabbitmq_service


@router.post("/send_nebula", response_model=MessageResponse)
async def send_nebula_message(request: NebulaOperationMessage):
    """发送消息到 Nebula 队列"""
    return await _send_to_queue(request, common_settings.rabbitmq_queue_nebula)


async def _send_to_queue(request: Union[NebulaOperationMessage], queue_name: str) -> MessageResponse:
    try:
        rabbitmq = get_rabbitmq_service()
        message_id = rabbitmq.publish_message(
            request.space_name, request.operation, request.data, queue_name=queue_name
        )

        logger.info(
            "Message sent: %s, operation: %s, queue: %s",
            message_id,
            request.operation,
            queue_name,
        )

        return MessageResponse(
            success=True,
            message_id=message_id,
            message=f"Message sent to queue successfully: {queue_name}",
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))