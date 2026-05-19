from typing import Optional

from pydantic import Field

from settings.base import EnvSettings


class WorkerSettings(EnvSettings):
    worker_debug: Optional[bool] = Field(alias="WORKER_DEBUG")


worker_settings = WorkerSettings()
