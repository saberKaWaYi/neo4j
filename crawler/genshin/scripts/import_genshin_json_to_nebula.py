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
    log_path = Path(__file__).resolve().parent / "import_genshin_json_to_nebula.log"
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

import json

from services.nebula_service import NebulaService

NEBULA_HOST = "172.25.241.218"
NEBULA_PORT = 9669
NEBULA_USERNAME = "root"
NEBULA_PASSWORD = "nebula"
SPACE_NAME = "genshin"
TAG_NAME = "Character"
EDGE_NAME = "Character_to_Character"
JSON_PATH = Path(__file__).resolve().parent / "genshin_network.json"


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    logger.info("JSON loaded successfully")
    return payload


def import_json_to_nebula() -> None:
    logger.info("Loading JSON from %s", JSON_PATH)
    payload = _load_json(JSON_PATH)

    nodes = payload["nodes"]
    edges = payload["edges"]

    svc = NebulaService(
        host=NEBULA_HOST,
        port=NEBULA_PORT,
        username=NEBULA_USERNAME,
        password=NEBULA_PASSWORD,
    )
    svc.connect()
    try:
        created_nodes = svc.add_nodes(SPACE_NAME, TAG_NAME, nodes)
        created_edges = svc.add_edges(SPACE_NAME, EDGE_NAME, edges)
        logger.info("Import completed: nodes=%s, edges=%s", created_nodes, created_edges)
    except Exception as e:
        logger.error("Import failed: %s", e)
        raise
    finally:
        svc.close()


if __name__ == "__main__":
    import_json_to_nebula()