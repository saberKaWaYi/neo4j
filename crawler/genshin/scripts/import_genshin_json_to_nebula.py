from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import json
import logging

from services.nebula_service import NebulaService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Hard-coded script config
NEBULA_HOST = "graphd"
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
        name_en = str(row.get("name_en", "")).strip()
        if not name_en:
            continue
        nodes.append(
            {
                "vid": name_en,
                "properties": {
                    "photo": str(row.get("photo", "")),
                    "name_zh": str(row.get("name_zh", "")),
                    "name_en": name_en,
                },
            }
        )
    return nodes


def _build_edges(social_network: list[dict]) -> list[dict]:
    edges = []
    for row in social_network:
        source_vid = str(row.get("name_en", "")).strip()
        title_en = str(row.get("title_en", "")).strip()
        title_zh = str(row.get("title_zh", "")).strip()
        source_name_zh = str(row.get("name_zh", "")).strip()

        if not source_vid or " about " not in title_en:
            continue

        target_vid = title_en.split(" about ", 1)[1].strip()
        if not target_vid:
            continue

        target_name_zh = ""
        if "关于" in title_zh:
            target_name_zh = title_zh.split("关于", 1)[1].strip()

        edges.append(
            {
                "source_vid": source_vid,
                "target_vid": target_vid,
                "properties": {
                    "source_name_en": source_vid,
                    "target_name_en": target_vid,
                    "source_name_zh": source_name_zh,
                    "target_name_zh": target_name_zh,
                    "title_en": title_en,
                    "title_zh": title_zh,
                },
            }
        )
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
