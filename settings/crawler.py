from typing import Optional

from pydantic import Field

from settings.base import EnvSettings


class CrawlerSettings(EnvSettings):
    crawler_debug: Optional[bool] = Field(default=None, alias="CRAWLER_DEBUG")
    crawler_cookies: str = Field(..., alias="CRAWLER_COOKIES")
    crawler_headers: str = Field(..., alias="CRAWLER_HEADERS")
    crawler_time_sleep: int = Field(default=3, alias="CRAWLER_TIME_SLEEP")
    crawler_max_retries: int = Field(default=15, alias="CRAWLER_MAX_RETRIES")
    crawler_producer_url: str = Field(
        default="http://web:8000/api/v1/messages/send_nebula",
        alias="CRAWLER_PRODUCER_URL",
    )


crawler_settings = CrawlerSettings()
