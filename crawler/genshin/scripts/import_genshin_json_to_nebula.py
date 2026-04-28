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
    return payload


def _build_nodes(characters: list[dict]) -> list[dict]:
    nodes = []
    for row in characters:
        nodes.append(
            {
                "vid": row["name_en"],
                "properties": {
                    "photo": row["photo"],
                    "name_zh": row["name_zh"],
                    "name_en": row["name_en"],
                },
            }
        )
    return nodes


def _build_edges(social_network: list[dict]) -> list[dict]:
    edges = []
    for row in social_network:
        source_id = row["name_en"]
        target_id = row["title_en"].split(" about ", 1)[1].strip()
        edge_id = f"{source_id} to {target_id}"
        source_name_en = source_id
        target_name_en = target_id
        source_name_zh = row["name_zh"]
        target_name_zh = row["title_zh"].split("关于", 1)[1].strip()
        title_en = row["title_en"]
        title_zh = row["title_zh"]
        edges.append({
            "id": edge_id,
            "source_id": source_id,
            "target_id": target_id,
            "properties": {
                "source_name_en": source_name_en,
                "target_name_en": target_name_en,
                "source_name_zh": source_name_zh,
                "target_name_zh": target_name_zh,
                "title_en": title_en,
                "title_zh": title_zh,
            },
        })
    return edges


def import_json_to_nebula() -> None:
    logger.info("Loading JSON from %s", JSON_PATH)
    payload = _load_json(JSON_PATH)

    characters = payload.get("characters", [])
    social_network = payload.get("social_network", [])
    if not isinstance(characters, list) or not isinstance(social_network, list):
        raise ValueError("JSON fields 'characters' and 'social_network' must be arrays")

    nodes = _build_nodes(characters)
    edges = _build_edges(social_network)

    logger.info("Prepared %s nodes and %s edges", len(nodes), len(edges))

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
    finally:
        svc.close()


if __name__ == "__main__":
    import_json_to_nebula()