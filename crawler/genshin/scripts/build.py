from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import logging


def _setup_script_logging() -> None:
    log = logging.getLogger(__name__)
    if log.handlers:
        return
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_path = Path(__file__).resolve().parent / "build.log"
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(ch)
    log.setLevel(logging.DEBUG)
    log.propagate = False


_setup_script_logging()
logger = logging.getLogger(__name__)

from services.nebula_service import NebulaService
from settings_config import settings


def build() -> None:
    logger.info("Ensuring Nebula space exists: %s", "genshin")
    svc = NebulaService(
        host=settings.nebula_host,
        port=settings.nebula_port,
        username=settings.nebula_username,
        password=settings.nebula_password,
    )
    svc.connect()
    try:
        svc.create_space(space_name="genshin", partition_num=5, replica_factor=1, vid_type="FIXED_STRING(128)")
        svc.create_tag("genshin", "Character", {"photo": "string", "name_zh": "string", "name_en": "string"})
        svc.create_edge_type(
            "genshin",
            "Character_to_Character",
            {
                "source_name_en": "string",
                "target_name_en": "string",
                "source_name_zh": "string",
                "target_name_zh": "string",
                "content_en": "string",
                "content_zh": "string",
            },
        )
        logger.info("Nebula schema ready for space: %s", "genshin")
    finally:
        svc.close()


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:
        logger.exception("Failed to build Nebula schema: %s", exc)
        raise