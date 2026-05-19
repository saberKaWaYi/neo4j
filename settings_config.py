from settings.common import LogServiceName, common_settings
from settings.crawler import crawler_settings
from settings.web import web_settings
from settings.worker import worker_settings


class Settings:
    def get_service_debug(self, service: LogServiceName) -> bool:
        service_debug_map = {
            "web": web_settings.web_debug,
            "crawler": crawler_settings.crawler_debug,
            "worker": worker_settings.worker_debug,
        }
        service_debug = service_debug_map[service]
        if service_debug is None:
            return common_settings.debug
        return service_debug

    debug = common_settings.debug
    nebula_host = common_settings.nebula_host
    nebula_port = common_settings.nebula_port
    nebula_username = common_settings.nebula_username
    nebula_password = common_settings.nebula_password
    businesses = common_settings.businesses

    rabbitmq_host = common_settings.rabbitmq_host
    rabbitmq_port = common_settings.rabbitmq_port
    rabbitmq_username = common_settings.rabbitmq_username
    rabbitmq_password = common_settings.rabbitmq_password
    rabbitmq_queue_nebula = common_settings.rabbitmq_queue_nebula
    rabbitmq_queue_mongo = common_settings.rabbitmq_queue_mongo

    crawler_debug = crawler_settings.crawler_debug
    crawler_cookies = crawler_settings.crawler_cookies
    crawler_headers = crawler_settings.crawler_headers
    crawler_time_sleep = crawler_settings.crawler_time_sleep
    crawler_max_retries = crawler_settings.crawler_max_retries
    crawler_producer_url = crawler_settings.crawler_producer_url

    web_debug = web_settings.web_debug
    web_name = web_settings.web_name
    web_version = web_settings.web_version

    worker_debug = worker_settings.worker_debug


settings = Settings()
