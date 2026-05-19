from typing import Optional

from pydantic import Field

from settings.base import EnvSettings


class WebSettings(EnvSettings):
    web_debug: Optional[bool] = Field(default=None, alias="WEB_DEBUG")
    web_name: str = Field(default="Web Service", alias="WEB_NAME")
    web_version: str = Field(default="1.0", alias="WEB_VERSION")


web_settings = WebSettings()
