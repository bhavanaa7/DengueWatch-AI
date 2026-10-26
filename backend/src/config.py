"""Configuration loading; all paths are relative to the backend directory."""
from pathlib import Path
import yaml

BACKEND_DIR = Path(__file__).resolve().parents[1]


def load_config(path=None):
    path = Path(path) if path else BACKEND_DIR / "configs" / "config.yaml"
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    for key in ("raw_dir", "processed_dir", "artifacts_dir", "reports_dir"):
        cfg["paths"][key] = BACKEND_DIR / cfg["paths"][key]
    return cfg
