from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class NebulaOperationMessage(BaseModel):
    operation: Literal["add_nodes", "add_edges", "delete_nodes", "delete_edges"]
    data: dict = Field(..., description="Payload matched by operation type")


class NebulaOperationResponse(BaseModel):
    success: bool
    message_id: str
    message: str
    timestamp: datetime
