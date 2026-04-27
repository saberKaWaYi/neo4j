import logging

logger = logging.getLogger(__name__)

from typing import Literal, Optional

import uuid
from datetime import datetime, timezone

import json

import pika

ALLOWED_OPERATIONS = {"add_nodes", "add_edges", "delete_nodes", "delete_edges"}


class RabbitMQService:
    """RabbitMQ 消息队列服务"""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        queue_names: list[str],
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        if not queue_names:
            raise ValueError("queue_names must be provided and cannot be empty")
        names = [name.strip() for name in queue_names if name and name.strip()]
        if not names:
            raise ValueError("queue_names must include at least one non-empty queue name")
        self.queue_names = list(dict.fromkeys(names))
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None

    def connect(self) -> None:
        """建立RabbitMQ连接"""
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        for queue_name in self.queue_names:
            self._channel.queue_declare(queue=queue_name, durable=True)
        logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")

    def disconnect(self) -> None:
        """关闭RabbitMQ连接"""
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            logger.info("RabbitMQ connection closed")

    def publish_message(
        self,
        operation: Literal[ALLOWED_OPERATIONS],
        data: dict,
        queue_name: str,
    ) -> str:
        """发布消息到队列"""
        message_id = str(uuid.uuid4())
        target_queue = self.validate_queue_name(queue_name)
        message = {
            "message_id": message_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "data": data,
            "target_queue": target_queue,
        }

        if not self._channel:
            self.connect()

        self._channel.basic_publish(
            exchange="",
            routing_key=target_queue,
            body=json.dumps(message, ensure_ascii=False),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
                message_id=message_id,
            ),
        )

        logger.info(
            "Published message %s with operation %s to queue %s",
            message_id,
            operation,
            target_queue,
        )
        return message_id

    def consume_message(self, queue_name: str, auto_ack: bool = False) -> Optional[dict]:
        """从队列消费一条消息"""
        target_queue = self.validate_queue_name(queue_name)
        if not self._channel:
            self.connect()

        method_frame, properties, body = self._channel.basic_get(
            queue=target_queue, auto_ack=auto_ack
        )

        if method_frame is None:
            return None

        message = json.loads(body.decode("utf-8"))
        message["delivery_tag"] = method_frame.delivery_tag
        message["target_queue"] = target_queue
        return message

    def acknowledge_message(self, delivery_tag: int) -> None:
        """确认消息处理完成"""
        if self._channel:
            self._channel.basic_ack(delivery_tag=delivery_tag)
            logger.info(f"Acknowledged message with delivery_tag {delivery_tag}")

    def reject_message(self, delivery_tag: int, requeue: bool = True) -> None:
        """拒绝消息，可选择重新入队"""
        if self._channel:
            self._channel.basic_reject(delivery_tag=delivery_tag, requeue=requeue)
            logger.info(
                f"Rejected message with delivery_tag {delivery_tag}, requeue={requeue}"
            )

    def validate_queue_name(self, queue_name: str) -> str:
        target_queue = queue_name.strip()
        if not target_queue:
            raise ValueError("queue_name must be provided and cannot be empty")
        if target_queue not in self.queue_names:
            raise ValueError(f"queue_name {target_queue} is not valid")
        return target_queue