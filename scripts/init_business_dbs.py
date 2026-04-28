from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import logging


def _setup_script_logging() -> None:
    log = logging.getLogger(__name__)
    if log.handlers:
        return
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_path = Path(__file__).resolve().parent / "init_business_dbs.log"
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


from settings_config import settings

import subprocess


def run_all() -> None:
    for business in settings.businesses:
        build_script = _REPO_ROOT / "crawler" / business / "scripts" / "build.py"
        if not build_script.exists():
            raise FileNotFoundError(
                f"Build script not found for business {business!r}: {build_script}"
            )

        logger.info("Running build script for business: %s", business)
        subprocess.run(
            [sys.executable, str(build_script)],
            check=True,
            cwd=str(_REPO_ROOT),
        )
        logger.info("Build script succeeded for business: %s", business)


if __name__ == "__main__":
    run_all()