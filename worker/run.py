import logging
from logging_config import setup_logging

setup_logging("worker")
logger = logging.getLogger("worker")

from settings import common_settings

from services.rabbitmq_service import RabbitMQService
from services.nebula_service import NebulaService

import time

class QueueWorker:

    def __init__(self):
        self.rabbitmq = RabbitMQService(
            host=common_settings.rabbitmq_host,
            port=common_settings.rabbitmq_port,
            username=common_settings.rabbitmq_username,
            password=common_settings.rabbitmq_password,
            queue_names=[
                common_settings.rabbitmq_queue_nebula
            ]
        )
        self.nebula = NebulaService(
            host=common_settings.nebula_host,
            port=common_settings.nebula_port,
            username=common_settings.nebula_username,
            password=common_settings.nebula_password
        )
        self.queue_poll_order = [
            common_settings.rabbitmq_queue_nebula
        ]
        self.queue_handlers = {
            common_settings.rabbitmq_queue_nebula: self._handle_nebula_message
        }

    def run_forever(self) -> None:
        logger.info("Starting queue worker, queues=%s", self.rabbitmq.queue_names)
        self.rabbitmq.connect()
        self.nebula.connect()
        try:
            while True:
                has_message = False
                for queue_name in self.queue_poll_order:
                    message = self.rabbitmq.consume_message(
                        auto_ack=False,
                        queue_name=queue_name,
                    )
                    if message is None:
                        continue
                    has_message = True
                    self._dispatch_message(queue_name, message)
                if not has_message:
                    time.sleep(1.0)
        finally:
            self.rabbitmq.disconnect()
            self.nebula.close()

    def _dispatch_message(self, queue_name: str, message: dict) -> None:
        handler = self.queue_handlers.get(queue_name)
        delivery_tag = message.get("delivery_tag")
        if handler is None:
            logger.warning(
                "No handler for queue=%s message_id=%s; rejecting",
                queue_name,
                message.get("message_id"),
            )
            if delivery_tag:
                self.rabbitmq.reject_message(delivery_tag, requeue=False)
            return
        try:
            handler(message)
            if delivery_tag:
                self.rabbitmq.acknowledge_message(delivery_tag)
        except Exception as exc:
            logger.exception(
                "Worker failed queue=%s message_id=%s: %s",
                queue_name,
                message.get("message_id"),
                exc,
            )
            if delivery_tag:
                self.rabbitmq.reject_message(delivery_tag, requeue=False)

    def _handle_nebula_message(self, message: dict) -> None:
        space_name = message.get("space_name")
        operation = message.get("operation")
        data = message.get("data")
        result = self.nebula.execute_operation(space_name, operation, data)
        logger.info(
            "Nebula processed message_id=%s operation=%s result=%s",
            message.get("message_id"),
            operation,
            result,
        )


def run_worker() -> None:
    worker = QueueWorker()
    worker.run_forever()