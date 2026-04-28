from pydantic import BaseModel, Field
from typing import Literal

import uuid
from datetime import datetime


class NebulaOperationMessage(BaseModel):
    operation: Literal["add_nodes", "add_edges", "delete_nodes", "delete_edges"]
    data: dict = Field(..., description="Payload matched by operation type")


class NebulaOperationResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the message")