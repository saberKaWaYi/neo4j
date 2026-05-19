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
    log_path = Path(__file__).resolve().parent / "send_genshin_json_to_web.log"
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
import requests

from settings import crawler_settings

SPACE_NAME = "genshin"
TAG_NAME = "Character"
EDGE_NAME = "Character_to_Character"
JSON_PATH = Path(__file__).resolve().parent / "genshin_network.json"
WEB_SEND_URL = crawler_settings.crawler_producer_url


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    logger.info("JSON loaded successfully")
    return payload


def send_json_to_web() -> None:
    logger.info("Loading JSON from %s", JSON_PATH)
    payload = _load_json(JSON_PATH)

    nodes = payload["nodes"]
    edges = payload["edges"]

    payload_nodes = {
        "space_name": SPACE_NAME,
        "operation": "add_nodes",
        "data": {"tag": TAG_NAME, "nodes": nodes},
    }
    payload_edges = {
        "space_name": SPACE_NAME,
        "operation": "add_edges",
        "data": {"edge_type": EDGE_NAME, "edges": edges},
    }

    try:
        logger.info("Sending nodes to web: %s", WEB_SEND_URL)
        response_nodes = requests.post(WEB_SEND_URL, json=payload_nodes, timeout=30)
        response_nodes.raise_for_status()
        logger.info("Nodes sent successfully: status=%s body=%s", response_nodes.status_code, response_nodes.text)

        logger.info("Sending edges to web: %s", WEB_SEND_URL)
        response_edges = requests.post(WEB_SEND_URL, json=payload_edges, timeout=30)
        response_edges.raise_for_status()
        logger.info("Edges sent successfully: status=%s body=%s", response_edges.status_code, response_edges.text)

        logger.info("All requests finished: nodes=%s edges=%s", len(nodes), len(edges))
    except Exception as e:
        logger.error("Send failed: %s", e)
        raise


if __name__ == "__main__":
    send_json_to_web()
